"use client";

import { useEffect, useState } from "react";
import { Frase, createFrase, deleteFrase, listFrases, updateFrase } from "@/lib/api";

export default function Home() {
  const [frases, setFrases] = useState<Frase[]>([]);
  const [novoTexto, setNovoTexto] = useState("");
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [textoEdicao, setTextoEdicao] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  async function carregar() {
    try {
      setFrases(await listFrases());
    } catch {
      setErro("falha ao carregar frases");
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch on mount, external data source
    carregar();
  }, []);

  async function handleCriar(e: React.FormEvent) {
    e.preventDefault();
    if (!novoTexto.trim()) return;
    try {
      await createFrase(novoTexto);
      setNovoTexto("");
      setErro(null);
      await carregar();
    } catch {
      setErro("falha ao criar frase");
    }
  }

  function iniciarEdicao(frase: Frase) {
    setEditandoId(frase.id);
    setTextoEdicao(frase.texto);
  }

  async function handleSalvarEdicao(id: number) {
    if (!textoEdicao.trim()) return;
    try {
      await updateFrase(id, textoEdicao);
      setEditandoId(null);
      setErro(null);
      await carregar();
    } catch {
      setErro("falha ao editar frase");
    }
  }

  async function handleDeletar(id: number) {
    try {
      await deleteFrase(id);
      setErro(null);
      await carregar();
    } catch {
      setErro("falha ao deletar frase");
    }
  }

  return (
    <main style={{ maxWidth: 600, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Cadastro de Frases</h1>

      {erro && <p style={{ color: "red" }}>{erro}</p>}

      <form onSubmit={handleCriar} style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        <input
          value={novoTexto}
          onChange={(e) => setNovoTexto(e.target.value)}
          placeholder="Nova frase"
          style={{ flex: 1 }}
        />
        <button type="submit">Adicionar</button>
      </form>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {frases.map((frase) => (
          <li key={frase.id} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            {editandoId === frase.id ? (
              <>
                <input
                  value={textoEdicao}
                  onChange={(e) => setTextoEdicao(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button onClick={() => handleSalvarEdicao(frase.id)}>Salvar</button>
                <button onClick={() => setEditandoId(null)}>Cancelar</button>
              </>
            ) : (
              <>
                <span style={{ flex: 1 }}>{frase.texto}</span>
                <button onClick={() => iniciarEdicao(frase)}>Editar</button>
                <button onClick={() => handleDeletar(frase.id)}>Deletar</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}
