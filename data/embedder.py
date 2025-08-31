from typing import List, Union
import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM, BertConfig

# Default: 32k long-context retrieval encoder; swap to 2k/8k variants if you want lighter memory use
MODEL_ID = "hazyresearch/M2-BERT-32K-Retrieval-Encoder-V1"
MAX_LEN  = 32768  # must not exceed the model’s context length

class M2Embedder:
    def __init__(self, model_id: str = MODEL_ID, max_len: int = MAX_LEN, device: Union[str, torch.device] = None):
        self.max_len = max_len
        self.device = device or "cpu"

        # Per model card: use bert-base-uncased tokenizer; trust_remote_code to enable sentence_embedding output
        self.config = BertConfig.from_pretrained(model_id)
        self.model = AutoModelForMaskedLM.from_pretrained(
            model_id, config=self.config, trust_remote_code=True
        ).to(self.device).eval()
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased", model_max_length=max_len)
    @torch.inference_mode()
    def __call__(self, texts: Union[str, List[str]]) -> torch.Tensor:
        if isinstance(texts, str):
            texts = [texts]

        batch = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_len,
            return_token_type_ids=False,
        ).to(self.device)
        # Model returns a dict with 'sentence_embedding' for the retrieval encoder
        out = self.model(**batch)
        emb = out["sentence_embedding"]          # shape: (batch, 768)
        # return as CPU float32 tensor; convert to numpy if you prefer: emb.cpu().numpy()
        return emb.detach().cpu()

# ---- usage ----
# if __name__ == "__main__":
#     embedder1 = M2Embedder()
#     vecs = embedder1(["hello world", "long text ..."])
#     print(vecs.shape)  # (2, 768)