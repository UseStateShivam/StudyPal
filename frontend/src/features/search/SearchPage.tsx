import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { Course, SearchResponse } from '../../types';
import { Search, SlidersHorizontal, BookOpen, ExternalLink, Sparkles } from 'lucide-react';

export const SearchPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [query, setQuery] = useState('How does gradient descent optimize parameters?');
  const [method, setMethod] = useState<'hybrid' | 'tfidf' | 'embedding'>('hybrid');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const res = await api.get<Course[]>('/courses');
      setCourses(res.data);
      if (res.data.length > 0) {
        setSelectedCourse(res.data[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !selectedCourse) return;
    setLoading(true);
    try {
      const res = await api.post<SearchResponse>(`/courses/${selectedCourse.id}/search`, {
        query,
        retrieval_method: method,
        top_k: 5,
      });
      setResults(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Question Retrieval & Note Grounding</h1>
        <p className="text-sm text-slate-400 mt-1">
          Zero-hallucination search. Retrieves exact passages extracted from your course notes using lexical and semantic representations.
        </p>
      </div>

      {/* Search Input Box */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-4 top-3.5 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your notes (e.g. What is the difference between supervised and unsupervised learning?)"
              className="w-full pl-12 pr-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500 transition"
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400 flex items-center">
                <SlidersHorizontal className="w-3.5 h-3.5 mr-1" />
                Mode:
              </span>
              {(['hybrid', 'tfidf', 'embedding'] as const).map((m) => (
                <button
                  type="button"
                  key={m}
                  onClick={() => setMethod(m)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium uppercase tracking-wider transition cursor-pointer border ${
                    method === m
                      ? 'bg-sky-500/20 text-sky-300 border-sky-500/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  {m === 'hybrid' ? 'Hybrid (Fused)' : m === 'tfidf' ? 'TF-IDF' : 'Dense Embedding'}
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-sky-600/30 transition disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Searching...' : 'Search Passages'}
            </button>
          </div>
        </form>
      </div>

      {/* Results Section */}
      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>
              Found <strong className="text-white">{results.total_results}</strong> relevant passages for "{results.query}"
            </span>
            <span className="uppercase tracking-wider font-semibold text-sky-400">
              Retrieval Strategy: {results.retrieval_method_used}
            </span>
          </div>

          {results.results.length === 0 ? (
            <div className="text-center py-12 bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-sm">
              No passages found matching your query. Try broadening your keywords.
            </div>
          ) : (
            results.results.map((item, idx) => (
              <div
                key={item.chunk_id || idx}
                className="bg-slate-900 border border-slate-800 p-5 rounded-2xl hover:border-slate-700 transition"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 bg-slate-800 rounded-md text-sky-400">
                      <BookOpen className="w-4 h-4" />
                    </span>
                    <span className="text-sm font-bold text-white">{item.document_title}</span>
                    {item.page_number && (
                      <span className="text-xs text-slate-500">Page {item.page_number}</span>
                    )}
                  </div>
                  <span className="text-xs font-mono font-semibold px-2 py-0.5 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-md">
                    Score: {item.similarity_score}
                  </span>
                </div>

                <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 font-serif">
                  "{item.passage}"
                </p>

                {item.topic_label && (
                  <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                    <span>Topic: <strong className="text-slate-400">{item.topic_label}</strong></span>
                    <span>Direct source excerpt</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
