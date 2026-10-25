import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';
import { Course, RecommendationResponse } from '../../types';
import {
  BookOpen,
  Layers,
  Sparkles,
  HelpCircle,
  TrendingUp,
  ArrowRight,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [activeCourse, setActiveCourse] = useState<Course | null>(null);
  const [recs, setRecs] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const courseRes = await api.get<Course[]>('/courses');
      setCourses(courseRes.data);
      if (courseRes.data.length > 0) {
        const first = courseRes.data[0];
        setActiveCourse(first);
        const recRes = await api.get<RecommendationResponse>(`/courses/${first.id}/recommendations`);
        setRecs(recRes.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500 mr-3" />
        Loading dashboard metrics...
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="text-center py-16 bg-slate-900/60 border border-slate-800 rounded-3xl p-8 max-w-xl mx-auto mt-10">
        <BookOpen className="w-12 h-12 text-sky-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">No courses found yet</h2>
        <p className="text-slate-400 mb-6 text-sm">
          Get started by creating your first course and uploading notes or lecture slides.
        </p>
        <Link
          to="/courses"
          className="inline-flex items-center px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-xl transition shadow-lg shadow-sky-600/30"
        >
          Create Course
          <ArrowRight className="ml-2 w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-sky-950/60 to-slate-900 border border-sky-500/20 p-6 rounded-2xl">
        <div>
          <span className="px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider bg-sky-500/20 text-sky-300 rounded-full">
            Active Study Course
          </span>
          <h1 className="text-2xl font-extrabold text-white mt-1.5">{activeCourse?.name}</h1>
          <p className="text-slate-400 text-sm mt-1">{activeCourse?.description || 'Curriculum notes & personalized revision'}</p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/quiz"
            className="inline-flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 transition"
          >
            <HelpCircle className="w-4 h-4 mr-2 text-sky-400" />
            Take Diagnostic Quiz
          </Link>
          <Link
            to="/recommendations"
            className="inline-flex items-center px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-sky-600/30 transition"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Revision Plan
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Documents</span>
            <BookOpen className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">{activeCourse?.document_count || 0}</div>
          <p className="text-xs text-slate-500 mt-1">Uploaded & indexed</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Discovered Topics</span>
            <Layers className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">{activeCourse?.topic_count || 0}</div>
          <p className="text-xs text-slate-500 mt-1">K-Means clusters</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Status</span>
            <TrendingUp className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white capitalize">
            {recs?.is_cold_start ? 'Cold Start' : 'Personalised'}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {recs?.is_cold_start ? 'No quiz attempts yet' : 'BKT active'}
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Top Revision Priority</span>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-lg font-bold text-white truncate">
            {recs?.recommendations[0]?.topic_label || 'All Topics Up-to-Date'}
          </div>
          <p className="text-xs text-slate-500 mt-1">Based on mastery & recency</p>
        </div>
      </div>

      {/* Recommended Topics Preview */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-bold text-white">Recommended Revision Focus</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Ground-truth study recommendations fused from Bayesian Knowledge Tracing and content relevance.
            </p>
          </div>
          <Link
            to="/recommendations"
            className="text-xs font-medium text-sky-400 hover:text-sky-300 inline-flex items-center"
          >
            View Complete Plan <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>

        <div className="space-y-3">
          {recs?.recommendations.slice(0, 3).map((item) => (
            <div
              key={item.topic_id}
              className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-bold flex items-center justify-center">
                    #{item.priority_rank}
                  </span>
                  <span className="font-semibold text-white text-sm">{item.topic_label}</span>
                  <span className="text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded">
                    Score: {item.revision_score}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1 pl-8">{item.primary_reason}</p>
              </div>

              <div className="flex items-center gap-4 shrink-0 pl-8 md:pl-0">
                <div className="text-right">
                  <div className="text-xs text-slate-400">Mastery Est.</div>
                  <div className="text-sm font-bold text-white">
                    {(item.mastery_probability * 100).toFixed(0)}%
                  </div>
                </div>
                <Link
                  to="/quiz"
                  className="px-3.5 py-1.5 bg-sky-600/20 hover:bg-sky-600 text-sky-300 hover:text-white border border-sky-500/30 text-xs font-medium rounded-lg transition"
                >
                  Practice Topic
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
