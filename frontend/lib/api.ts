const API_URL = "http://localhost:8000";

export interface Frase {
  id: number;
  texto: string;
  criado_em: string;
}

export async function listFrases(): Promise<Frase[]> {
  const res = await fetch(`${API_URL}/frases`);
  if (!res.ok) throw new Error("falha ao listar frases");
  return res.json();
}

export async function createFrase(texto: string): Promise<Frase> {
  const res = await fetch(`${API_URL}/frases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!res.ok) throw new Error("falha ao criar frase");
  return res.json();
}

export async function updateFrase(id: number, texto: string): Promise<Frase> {
  const res = await fetch(`${API_URL}/frases/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!res.ok) throw new Error("falha ao editar frase");
  return res.json();
}

export async function deleteFrase(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/frases/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("falha ao deletar frase");
}
