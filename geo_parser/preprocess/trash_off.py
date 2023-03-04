from transformers import AutoTokenizer

text_column_name = 'text'
tokenizer = AutoTokenizer.from_pretrained('<path>', model_max_length=512)
trash_cutoff = 0.3


def filtering_rule(examples):
    tokenized = tokenizer(examples[text_column_name])["input_ids"]
    return [len(t) < trash_cutoff * len(e) for t, e in zip(tokenized, examples[text_column_name])]
