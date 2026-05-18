"use client";
import { useState } from "react";

export default function Home() {
  const [image, setImage] = useState("");
  const [prompt, setPrompt] = useState("");
  const [selectedCulture, setSelectedCulture] = useState("");
  const [result, setResult] = useState("");

  const generate = async () => {
    const res = await fetch("http://127.0.0.1:8000/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt, culture: selectedCulture }),
    });

    const data = await res.json();

    setResult(JSON.stringify(data, null, 2));

    if (data.image) {
      setImage(data.image);
    }
  };

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-4">LIMANEX</h1>

      <input
        className="border p-2 w-full mb-4"
        placeholder="Prompt yaz"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <input
        className="border p-2 w-full mb-4"
        placeholder="Culture (Japanese vs)"
        value={selectedCulture}
        onChange={(e) => setSelectedCulture(e.target.value)}
      />

      <button
        onClick={generate}
        className="bg-black text-white px-4 py-2"
      >
        Generate
      </button>

      <pre className="mt-4">{result}</pre>

      {image && (
        <img src={image} className="mt-6 rounded" />
      )}
    </div>
  );
}