import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';
import { Course, RecommendationResponse } from '../../types';
import { Sparkles, BookOpen, HelpCircle, CheckCircle, ArrowRight, Info } from 'lucide-react';

export const RecommendationsPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const res = await api.get<Course[]>('/courses');
      setCourses(res.data);
      if (res.data.length > 0) {
        selectCourse(res.data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const selectCourse = async (course: Course) => {
    setSelectedCourse(course);
    try {
      const res = await api.get<RecommendationResponse>(`/courses/${course.id}/recommendations`);
      setData(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Intelligent Study Recommendation Plan</h1>
        <p className="text-sm text-slate-400 mt-1">
          Ranked revision topics fusing BKT mastery, weakness classifier predictions, and time since practice.
        </p>
      </div>

      {data && (
        <>
          {/* Mode Badge */}
          <div className="flex items-center justify-between p-4 bg-slate-900 border border-slate-800 rounded-2xl">
            <div className="flex items-center gap-3">
              <span className="p-2 bg-sky-500/10 rounded-lg text-sky-400">
                <Sparkles className="w-5 h-5" />
              </span>
              <div>
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Recommender Status
                </div>
                <div className="text-sm font-bold text-white capitalize">
                  {data.recommendation_mode} Recommendation Engine
                </div>
              </div>
            </div>

            {data.is_cold_start ? (
              <span className="text-xs bg-amber-500/10 border border-amber-500/20 text-amber-300 px-3 py-1 rounded-full flex items-center">
                <Info className="w-3.5 h-3.5 mr-1.5" />
                Cold-Start (Take quizzes to unlock personalized predictions)
              </span>
            ) : (
              <span className="text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-3 py-1 rounded-full flex items-center">
                <CheckCircle className="w-3.5 h-3.5 mr-1.5" />
                Personalised to your quiz history
              </span>
            )}
          </div>

          {/* Recommendations List */}
          <div className="space-y-6">
            {data.recommendations.map((item) => (
              <div
                key={item.topic_id}
                className="bg-slate-900 border border-slate-800 p-6 md:p-8 rounded-2xl shadow-xl space-y-5"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 rounded-xl bg-sky-500/10 border border-sky-500/30 text-sky-400 font-extrabold text-sm flex items-center justify-center shrink-0">
                      #{item.priority_rank}
                    </span>
                    <div>
                      <h2 className="text-lg font-bold text-white">{item.topic_label}</h2>
                      <p className="text-xs text-sky-400 font-medium mt-0.5">{item.primary_reason}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    <div className="text-right">
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Priority Score</div>
                      <div className="text-sm font-mono font-bold text-amber-400">{item.revision_score}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">BKT Mastery</div>
                      <div className="text-sm font-mono font-bold text-sky-400">
                        {(item.mastery_probability * 100).toFixed(0)}%
                      </div>
                    </div>
                    <Link
                      to="/quiz"
                      className="inline-flex items-center px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-sky-600/30 transition"
                    >
                      <HelpCircle className="w-3.5 h-3.5 mr-1.5" />
                      Quiz Topic
                    </Link>
                  </div>
                </div>

                {/* Grounded Note Passages */}
                <div>
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center">
                    <BookOpen className="w-3.5 h-3.5 mr-1.5 text-sky-400" />
                    Review Relevant Material from Notes:
                  </h3>
                  <div className="space-y-2">
                    {item.suggested_passages.map((p, idx) => (
                      <div
                        key={p.chunk_id || idx}
                        className="p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl text-xs text-slate-300 leading-relaxed font-serif"
                      >
                        <div className="text-[11px] font-sans font-semibold text-sky-400 mb-1">
                          Source: {p.document_title}
                        </div>
                        "{p.passage}"
                      </div>
                    ))}
                  </div>
                </div>

                {/* Score Breakdown Transparency */}
                <div className="pt-2 flex flex-wrap gap-4 text-[11px] text-slate-500 border-t border-slate-800/60">
                  <span>Score breakdown:</span>
                  <span>Mastery component: <strong className="text-slate-400">{item.contributing_scores.mastery_weight_contrib}</strong></span>
                  <span>Weakness component: <strong className="text-slate-400">{item.contributing_scores.weakness_weight_contrib}</strong></span>
                  <span>Recency factor: <strong className="text-slate-400">{item.contributing_scores.recency_weight_contrib}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
