import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { Course, TopicItem } from '../../types';
import { Layers, Edit2, Check, BookOpen, Tag } from 'lucide-react';

export const TopicsPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingTopicId, setEditingTopicId] = useState<string | null>(null);
  const [editLabel, setEditLabel] = useState('');

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
      const res = await api.get<TopicItem[]>(`/courses/${course.id}/topics`);
      setTopics(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveLabel = async (topicId: string) => {
    if (!editLabel.trim()) return;
    try {
      const res = await api.patch<TopicItem>(`/topics/${topicId}`, { label: editLabel });
      setTopics(topics.map((t) => (t.id === topicId ? res.data : t)));
      setEditingTopicId(null);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Discovered Topic Groups</h1>
        <p className="text-sm text-slate-400 mt-1">
          Unsupervised K-Means clustering discovers concept groupings from your notes. You can customize labels anytime.
        </p>
      </div>

      {courses.length > 1 && (
        <div className="flex gap-2 pb-2 overflow-x-auto">
          {courses.map((c) => (
            <button
              key={c.id}
              onClick={() => selectCourse(c)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition cursor-pointer shrink-0 ${
                selectedCourse?.id === c.id
                  ? 'bg-sky-600 text-white'
                  : 'bg-slate-900 text-slate-300 hover:bg-slate-800'
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {topics.map((topic) => (
          <div
            key={topic.id}
            className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between hover:border-slate-700 transition"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">
                  Cluster #{topic.cluster_index}
                </span>
                <span className="text-xs text-slate-500">{topic.chunk_count} passages</span>
              </div>

              {editingTopicId === topic.id ? (
                <div className="flex items-center gap-2 mb-3">
                  <input
                    type="text"
                    value={editLabel}
                    onChange={(e) => setEditLabel(e.target.value)}
                    className="w-full px-3 py-1 bg-slate-950 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-sky-500"
                    autoFocus
                  />
                  <button
                    onClick={() => handleSaveLabel(topic.id)}
                    className="p-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between group mb-3">
                  <h3 className="text-base font-bold text-white group-hover:text-sky-300 transition truncate mr-2">
                    {topic.label}
                  </h3>
                  <button
                    onClick={() => {
                      setEditingTopicId(topic.id);
                      setEditLabel(topic.label);
                    }}
                    className="text-slate-500 hover:text-slate-300 p-1 transition"
                    title="Edit topic label"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {topic.keywords && (
                <div className="mb-4">
                  <div className="flex items-center text-xs font-semibold text-slate-400 mb-1.5">
                    <Tag className="w-3.5 h-3.5 mr-1 text-slate-500" />
                    Top TF-IDF Keywords:
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {topic.keywords.split(',').map((kw, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 bg-slate-950 border border-slate-800 text-[11px] text-slate-300 rounded-md"
                      >
                        {kw.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
              <span>{topic.is_custom_label ? 'Custom Label' : 'Auto-generated'}</span>
              <span>K-Means++</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
