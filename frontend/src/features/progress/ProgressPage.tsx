import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { Course, CourseProgressOverview } from '../../types';
import {
  TrendingUp,
  Award,
  CheckCircle,
  Clock,
  BarChart2,
  Calendar
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export const ProgressPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [progress, setProgress] = useState<CourseProgressOverview | null>(null);
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
      const res = await api.get<CourseProgressOverview>(`/courses/${course.id}/progress`);
      setProgress(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Student Mastery & Progress Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">
          Bayesian Knowledge Tracing (BKT) dynamically estimates concept mastery over practice history.
        </p>
      </div>

      {progress && (
        <>
          {/* Progress KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                Overall Course Mastery
              </div>
              <div className="text-3xl font-extrabold text-sky-400">
                {(progress.overall_mastery * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-slate-500 mt-1">Average across topics</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                Quiz Sessions
              </div>
              <div className="text-3xl font-extrabold text-white">
                {progress.total_quizzes_taken}
              </div>
              <p className="text-xs text-slate-500 mt-1">Completed practice runs</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                Questions Answered
              </div>
              <div className="text-3xl font-extrabold text-white">
                {progress.total_questions_answered}
              </div>
              <p className="text-xs text-slate-500 mt-1">Total recorded attempts</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
                Overall Accuracy
              </div>
              <div className="text-3xl font-extrabold text-emerald-400">
                {progress.overall_accuracy.toFixed(1)}%
              </div>
              <p className="text-xs text-slate-500 mt-1">Correct answer ratio</p>
            </div>
          </div>

          {/* Topic-Level Breakdown Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-lg font-bold text-white mb-4">Topic Mastery Breakdown</h2>
            <div className="space-y-4">
              {progress.topics_state.map((t) => (
                <div
                  key={t.topic_id}
                  className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-bold text-white truncate">{t.topic_label}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {t.total_attempts} attempts • {t.correct_attempts} correct
                      {t.last_practiced_at && ` • Last practiced ${new Date(t.last_practiced_at).toLocaleDateString()}`}
                    </p>
                  </div>

                  <div className="flex items-center gap-4 shrink-0">
                    <div className="w-32 bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-sky-500 h-full rounded-full transition-all duration-300"
                        style={{ width: `${t.mastery_probability * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-mono font-bold text-white w-12 text-right">
                      {(t.mastery_probability * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Timeline Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-lg font-bold text-white mb-2">Mastery Trajectory Over Time</h2>
            <p className="text-xs text-slate-400 mb-6">
              Empirical progression of BKT mastery probability after consecutive quiz responses.
            </p>

            {progress.mastery_timeline.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">
                No quiz responses recorded yet. Take a quiz to populate mastery progression trends.
              </div>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={progress.mastery_timeline.map((pt, i) => ({
                      index: i + 1,
                      mastery: Math.round(pt.mastery * 100),
                      label: pt.topic_label,
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="index" stroke="#64748b" tick={{ fontSize: 12 }} />
                    <YAxis stroke="#64748b" domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                      itemStyle={{ color: '#38bdf8' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="mastery"
                      stroke="#0284c7"
                      strokeWidth={2.5}
                      dot={{ fill: '#38bdf8', r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
