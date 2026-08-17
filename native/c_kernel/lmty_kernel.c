#include "lmty_kernel.h"
#include <string.h>

typedef struct { const char *kind; const char *word; unsigned context; unsigned tools; } rule;

static const rule RULES[] = {
    {"visual_ui", "visual", 280, 4},
    {"visual_ui", "layout", 280, 4},
    {"visual_ui", "css", 280, 4},
    {"bug", "bug", 320, 5},
    {"bug", "erro", 320, 5},
    {"bug", "debug", 320, 5},
    {"performance", "performance", 300, 4},
    {"performance", "bundle", 300, 4},
    {"accessibility", "aria", 260, 4},
    {"accessibility", "a11y", 260, 4},
    {"accessibility", "teclado", 260, 4}
};

static const rule *find_rule(const char *text) {
    size_t count = sizeof(RULES) / sizeof(RULES[0]);
    size_t index;
    for (index = 0; index < count; index++) {
        if (strstr(text, RULES[index].word) != NULL) return &RULES[index];
    }
    return NULL;
}

const char *lmty_classify(const char *text) {
    const rule *match = find_rule(text);
    return match == NULL ? "general" : match->kind;
}

lmty_decision lmty_decide(const char *text) {
    const rule *match = find_rule(text);
    lmty_decision decision = {"general", 420, 8};
    if (match != NULL) {
        decision.kind = match->kind;
        decision.context_budget = match->context;
        decision.tool_budget = match->tools;
    }
    return decision;
}
