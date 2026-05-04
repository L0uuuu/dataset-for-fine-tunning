import json
import re
from typing import List, Dict, Any, Tuple

# Canonical system prompts
SYSTEM_PROMPT_AR = (
    "أنتَ مساعد قانوني متخصص في القانون التونسي، تابع لمنصة E-Tafakna. "
    "أجب فقط استناداً إلى الوثائق المقدَّمة. إذا تجاوز السؤال محتوى الوثائق، "
    "وضّح ذلك صراحةً وأوصِ باستشارة مختص. نظّم إجابتك حسب الإشكالية القانونية. "
    "استشهد دائماً بالفصل والمصدر. هذا لا يُشكّل استشارة قانونية مهنية."
)

SYSTEM_PROMPT_FR = (
    "Vous êtes un assistant juridique de la plateforme E-Tafakna, spécialisé dans le droit tunisien. "
    "Répondez uniquement à partir des documents fournis. Si une question dépasse "
    "le contenu des documents, indiquez-le clairement et recommandez de consulter "
    "un professionnel. Structurez votre réponse par problématique juridique. "
    "Citez toujours les articles et sources. Ceci ne constitue pas un avis juridique professionnel."
)

ARABIC_RANGE = re.compile(r"[\u0600-\u06FF]")
LATIN_RANGE = re.compile(r"[A-Za-zÀ-ÿ]")

def detect_language(system_text: str) -> Tuple[str, str]:
    """
    Detect language of the system prompt.
    Returns (language, resolution_note).
    language: "ar" or "fr"
    resolution_note: description of how mixed case was resolved or "" if not mixed.
    """
    arabic_chars = ARABIC_RANGE.findall(system_text)
    latin_chars = LATIN_RANGE.findall(system_text)

    has_arabic = len(arabic_chars) > 0
    has_latin = len(latin_chars) > 0

    if has_arabic and has_latin:
        # Mixed: choose dominant script by count
        if len(arabic_chars) >= len(latin_chars):
            return "ar", f"mixed → arabic (arabic={len(arabic_chars)} ≥ latin={len(latin_chars)})"
        return "fr", f"mixed → french (latin={len(latin_chars)} > arabic={len(arabic_chars)})"

    if has_arabic:
        return "ar", ""
    return "fr", ""

def main() -> None:
    input_path = "constructed data/all_messages.json"
    output_path = "all_messages_cleaned.json"

    # Load dataset
    with open(input_path, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    total_records = 0
    arabic_count = 0
    french_count = 0
    mixed_resolution_notes: List[str] = []

    # Capture samples for before/after
    sample_ar_before = sample_ar_after = None
    sample_fr_before = sample_fr_after = None

    # Track original system prompt variants
    original_system_prompts = set()

    for record in data:
        total_records += 1
        system_msg = record["messages"][0]["content"]
        original_system_prompts.add(system_msg)

        lang, note = detect_language(system_msg)
        if note:
            mixed_resolution_notes.append(note)

        if lang == "ar":
            if sample_ar_before is None:
                sample_ar_before = system_msg
                sample_ar_after = SYSTEM_PROMPT_AR
            record["messages"][0]["content"] = SYSTEM_PROMPT_AR
            arabic_count += 1
        else:
            if sample_fr_before is None:
                sample_fr_before = system_msg
                sample_fr_after = SYSTEM_PROMPT_FR
            record["messages"][0]["content"] = SYSTEM_PROMPT_FR
            french_count += 1

    # Save cleaned dataset
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Summary report
    print("=== Summary Report ===")
    print(f"Total records processed: {total_records}")
    print(f"Records assigned Arabic prompt: {arabic_count}")
    print(f"Records assigned French prompt: {french_count}")

    if mixed_resolution_notes:
        print("Mixed-language resolution:")
        # Print unique notes in order of appearance
        seen = set()
        for note in mixed_resolution_notes:
            if note not in seen:
                print(f"  - {note}")
                seen.add(note)
    else:
        print("Mixed-language resolution: none detected")

    print(f"Original system prompt variants detected: {len(original_system_prompts)}")
    print("Confirmation: all original variants were replaced with canonical prompts.")

    print("\n=== Sample Before/After ===")
    if sample_ar_before is not None:
        print("\n[Arabic sample]")
        print("Before:", sample_ar_before)
        print("After :", sample_ar_after)
    if sample_fr_before is not None:
        print("\n[French sample]")
        print("Before:", sample_fr_before)
        print("After :", sample_fr_after)

if __name__ == "__main__":
    main()