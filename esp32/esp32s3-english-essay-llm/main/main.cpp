// ESP32-S3 offline English essay writer.
// Serial-only firmware: no Wi-Fi, API, display, or external storage.
// Generated model files: main/model_data.cpp and main/tok_data.cpp.

#include "llm.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

extern "C" const uint8_t MODEL_DATA[];
extern "C" const size_t MODEL_DATA_LEN;
extern "C" const uint8_t TOKENIZER_DATA[];
extern "C" const size_t TOKENIZER_DATA_LEN;

static const char* TAG = "essay_llm";
static constexpr int KV_SEQ_LEN = 72;
static constexpr int MAX_TOKENS = 256;
static constexpr int MAX_TOPIC_CHARS = 180;
static constexpr int MAX_GENERATION_TOKENS = 220;

static Transformer g_transformer{};
static Tokenizer g_tokenizer{};
static Sampler g_sampler{};

static float g_temperature = 0.72f;
static float g_top_p = 0.90f;
static uint64_t g_seed = 0x8E9D4A21ULL;

static bool init_model() {
  ESP_LOGI(TAG, "model bytes: %u", (unsigned)MODEL_DATA_LEN);
  ESP_LOGI(TAG, "tokenizer bytes: %u", (unsigned)TOKENIZER_DATA_LEN);
  ESP_LOGI(TAG, "internal heap before init: %u",
           (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL));

  if (!llm_init_embedded(&g_transformer, MODEL_DATA, MODEL_DATA_LEN, KV_SEQ_LEN)) {
    ESP_LOGE(TAG, "llm_init_embedded failed");
    return false;
  }

  if (!llm_tokenizer_from_memory(&g_tokenizer, TOKENIZER_DATA,
                                 TOKENIZER_DATA_LEN,
                                 g_transformer.config.vocab_size)) {
    ESP_LOGE(TAG, "tokenizer init failed");
    return false;
  }

  llm_build_sampler(&g_sampler, g_transformer.config.vocab_size,
                    g_temperature, g_top_p, g_seed);

  ESP_LOGI(TAG, "dim=%d hidden=%d layers=%d heads=%d vocab=%d ctx=%d",
           g_transformer.config.dim,
           g_transformer.config.hidden_dim,
           g_transformer.config.n_layers,
           g_transformer.config.n_heads,
           g_transformer.config.vocab_size,
           g_transformer.config.seq_len);
  ESP_LOGI(TAG, "internal heap after init: %u",
           (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
  return true;
}

static void trim_line(char* s) {
  size_t n = std::strlen(s);
  while (n && (s[n - 1] == '\r' || s[n - 1] == '\n' ||
               s[n - 1] == ' ' || s[n - 1] == '\t')) {
    s[--n] = '\0';
  }
  size_t start = 0;
  while (s[start] == ' ' || s[start] == '\t') ++start;
  if (start) std::memmove(s, s + start, std::strlen(s + start) + 1);
}

static void generate_essay(const char* topic) {
  char prompt[420];
  char topic_copy[MAX_TOPIC_CHARS + 1];

  std::strncpy(topic_copy, topic, MAX_TOPIC_CHARS);
  topic_copy[MAX_TOPIC_CHARS] = '\0';

  std::snprintf(prompt, sizeof(prompt),
                "User: Write a short English essay of about 120 words about %s.\nBot:",
                topic_copy);

  int tokens[MAX_TOKENS];
  int n_tokens = 0;
  llm_encode(&g_tokenizer, prompt, 0, 0, tokens, &n_tokens);

  if (n_tokens <= 0 || n_tokens >= MAX_TOKENS) {
    ESP_LOGE(TAG, "prompt produced %d tokens; reduce topic length", n_tokens);
    return;
  }

  int write_slot = 0;
  int abs_pos = 0;
  float* logits = nullptr;

  for (int i = 0; i < n_tokens; ++i) {
    if (write_slot >= KV_SEQ_LEN) {
      const int moved = llm_kv_slide(&g_transformer, KV_SEQ_LEN / 4, KV_SEQ_LEN / 4);
      if (moved <= 0) {
        ESP_LOGE(TAG, "KV slide failed while encoding prompt");
        return;
      }
      write_slot -= moved;
    }

    logits = llm_forward_at(&g_transformer, tokens[i], write_slot, abs_pos);
    ++write_slot;
    ++abs_pos;
  }

  llm_build_sampler(&g_sampler, g_transformer.config.vocab_size,
                    g_temperature, g_top_p, g_seed++);

  std::printf("\n--- essay ---\n");
  std::fflush(stdout);

  char scratch[512];
  int prev_token = tokens[n_tokens - 1];

  for (int step = 0; step < MAX_GENERATION_TOKENS; ++step) {
    if (write_slot >= KV_SEQ_LEN) {
      const int moved = llm_kv_slide(&g_transformer, KV_SEQ_LEN / 4, KV_SEQ_LEN / 4);
      if (moved <= 0) {
        ESP_LOGE(TAG, "KV slide failed during generation");
        break;
      }
      write_slot -= moved;
    }

    const int next_token = llm_sample(&g_sampler, logits);
    if (next_token == g_tokenizer.eos_id) break;

    const char* piece = llm_decode(&g_tokenizer, prev_token, next_token,
                                   scratch, sizeof(scratch));
    if (piece && *piece) {
      std::fputs(piece, stdout);
      std::fflush(stdout);
    }

    prev_token = next_token;
    logits = llm_forward_at(&g_transformer, next_token, write_slot, abs_pos);
    ++write_slot;
    ++abs_pos;
  }

  std::printf("\n--- end ---\n");
  std::printf("free internal heap: %u\n",
              (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
  std::fflush(stdout);
}

static void print_help() {
  std::printf(
      "\nESP32-S3 English Essay LLM\n"
      "Commands:\n"
      "  /help          show help\n"
      "  /temp 0.72     set temperature (0 = greedy)\n"
      "  /top_p 0.90    set nucleus sampling cutoff\n"
      "  /new           reset sampling settings\n"
      "\n"
      "Normal text is treated as an essay topic.\n"
      "Example: The importance of learning English\n\n");
}

extern "C" void app_main(void) {
  std::printf("\n========================================\n");
  std::printf(" ESP32-S3 OFFLINE ENGLISH ESSAY LLM\n");
  std::printf("========================================\n");

  if (!init_model()) {
    std::printf("MODEL INIT FAILED.\n");
    for (;;) vTaskDelay(pdMS_TO_TICKS(1000));
  }

  print_help();

  char line[256];
  while (true) {
    std::printf("\nessay> ");
    std::fflush(stdout);

    if (!std::fgets(line, sizeof(line), stdin)) {
      vTaskDelay(pdMS_TO_TICKS(20));
      continue;
    }

    trim_line(line);
    if (!line[0]) continue;

    if (!std::strcmp(line, "/help")) {
      print_help();
      continue;
    }

    if (!std::strncmp(line, "/temp ", 6)) {
      float v = std::strtof(line + 6, nullptr);
      if (v < 0.0f) v = 0.0f;
      if (v > 2.0f) v = 2.0f;
      g_temperature = v;
      std::printf("temperature = %.3f\n", g_temperature);
      continue;
    }

    if (!std::strncmp(line, "/top_p ", 7)) {
      float v = std::strtof(line + 7, nullptr);
      if (v < 0.01f) v = 0.01f;
      if (v > 1.0f) v = 1.0f;
      g_top_p = v;
      std::printf("top_p = %.3f\n", g_top_p);
      continue;
    }

    if (!std::strcmp(line, "/new")) {
      g_temperature = 0.72f;
      g_top_p = 0.90f;
      std::printf("sampling settings reset\n");
      continue;
    }

    generate_essay(line);
  }
}
