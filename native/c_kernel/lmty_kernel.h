#ifndef LMTY_KERNEL_H
#define LMTY_KERNEL_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    const char *kind;
    unsigned context_budget;
    unsigned tool_budget;
} lmty_decision;

lmty_decision lmty_decide(const char *text);
const char *lmty_classify(const char *text);

#ifdef __cplusplus
}
#endif

#endif
