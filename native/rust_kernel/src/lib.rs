#[derive(Debug, Clone, PartialEq)]
pub struct KernelDecision {
    pub kind: String,
    pub context_budget: u32,
    pub tool_budget: u32,
}

pub fn classify(text: &str) -> &'static str {
    let lower = text.to_ascii_lowercase();
    let rules = [
        ("visual_ui", ["visual", "layout", "css", "responsive"]),
        ("bug", ["bug", "erro", "falha", "debug"]),
        ("performance", ["performance", "lento", "bundle", "latencia"]),
        ("accessibility", ["a11y", "aria", "teclado", "contraste"]),
    ];
    rules.iter().find(|(_, words)| words.iter().any(|word| lower.contains(word))).map_or("general", |(kind, _)| *kind)
}

pub fn budget(kind: &str) -> (u32, u32) {
    match kind {
        "visual_ui" => (280, 4),
        "bug" => (320, 5),
        "performance" => (300, 4),
        "accessibility" => (260, 4),
        _ => (420, 8),
    }
}

pub fn decide(text: &str) -> KernelDecision {
    let kind = classify(text);
    let (context_budget, tool_budget) = budget(kind);
    KernelDecision { kind: kind.to_string(), context_budget, tool_budget }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn routes_visual_task() {
        assert_eq!(decide("fix responsive visual layout").kind, "visual_ui");
    }

    #[test]
    fn uses_general_budget() {
        assert_eq!(decide("explain architecture").tool_budget, 8);
    }
}
