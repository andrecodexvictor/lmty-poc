#include "lmty_kernel.h"
#include <assert.h>
#include <string.h>

int main(void) {
    lmty_decision visual = lmty_decide("visual responsive layout");
    lmty_decision general = lmty_decide("explain architecture");
    assert(strcmp(visual.kind, "visual_ui") == 0);
    assert(visual.context_budget == 280);
    assert(strcmp(general.kind, "general") == 0);
    assert(general.tool_budget == 8);
    return 0;
}
