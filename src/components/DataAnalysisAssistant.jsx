import React, { useState } from "react";

export default function DataAnalysisAssistant() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError("");
  };

  const handleQuestionChange = (e) => {
    setQuestion(e.target.value);
    setResult(null);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !question) {
      setError("CSVファイルをアップロードし、質問を入力してください");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("question", question);

    try {
      const res = await fetch("/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
      if (data.error) setError(data.error);
    } catch (err) {
      setError("リクエスト失敗：" + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded shadow mt-10">
      <h2 className="text-2xl font-bold mb-4">AIデータ分析アシスタント</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-700"
        />
        <textarea
          className="w-full border rounded p-2"
          rows={3}
          placeholder="データ分析の質問を入力してください 例：月別売上傾向グラフを描いてください"
          value={question}
          onChange={handleQuestionChange}
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? "分析中..." : "分析を依頼"}
        </button>
      </form>
      {error && (
        <div className="mt-4 text-red-600 font-semibold">{error}</div>
      )}
      {result && !error && (
        <div className="mt-6">
          <div className="text-lg font-semibold mb-2">分析結果：</div>
          <div className="mb-4 text-gray-800">{result.conclusion}</div>
          {result.chart && (
            <div className="mb-4">
              <div className="text-lg font-semibold mb-2">グラフ：</div>
              <div className="flex justify-center">
                <img
                  src={`data:image/png;base64,${result.chart}`}
                  alt="分析グラフ"
                  className="max-h-96 border rounded shadow"
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
