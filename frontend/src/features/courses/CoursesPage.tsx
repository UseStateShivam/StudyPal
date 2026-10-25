import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { Course, DocumentItem } from '../../types';
import {
  FolderPlus,
  Upload,
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle,
  Trash2,
  RefreshCw
} from 'lucide-react';

export const CoursesPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [newCourseName, setNewCourseName] = useState('');
  const [newCourseDesc, setNewCourseDesc] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const res = await api.get<Course[]>('/courses');
      setCourses(res.data);
      if (res.data.length > 0 && !selectedCourse) {
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
      const res = await api.get<DocumentItem[]>(`/courses/${course.id}/documents`);
      setDocuments(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCourseName.trim()) return;
    try {
      const res = await api.post<Course>('/courses', {
        name: newCourseName,
        description: newCourseDesc,
      });
      setNewCourseName('');
      setNewCourseDesc('');
      setCourses([res.data, ...courses]);
      selectCourse(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !selectedCourse) return;
    const file = e.target.files[0];
    setUploadError(null);
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post(`/courses/${selectedCourse.id}/documents`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      // Refresh documents
      selectCourse(selectedCourse);
    } catch (err: any) {
      setUploadError(err.response?.data?.detail?.message || 'File upload failed');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      await api.delete(`/documents/${docId}`);
      if (selectedCourse) selectCourse(selectedCourse);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Course Management & Document Library</h1>
        <p className="text-sm text-slate-400 mt-1">
          Create courses and upload lecture notes (.pdf or .txt) for automatic extraction and indexing.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Create & Select Courses */}
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center">
              <FolderPlus className="w-4 h-4 mr-2 text-sky-400" />
              New Course
            </h2>
            <form onSubmit={handleCreateCourse} className="space-y-3">
              <input
                type="text"
                placeholder="Course Name (e.g. Operating Systems)"
                value={newCourseName}
                onChange={(e) => setNewCourseName(e.target.value)}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:border-sky-500 focus:outline-none"
              />
              <textarea
                placeholder="Optional description"
                rows={2}
                value={newCourseDesc}
                onChange={(e) => setNewCourseDesc(e.target.value)}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:border-sky-500 focus:outline-none resize-none"
              />
              <button
                type="submit"
                className="w-full py-2 bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm rounded-xl transition"
              >
                Create Course
              </button>
            </form>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-3">Your Courses</h2>
            <div className="space-y-2">
              {courses.map((c) => (
                <div
                  key={c.id}
                  onClick={() => selectCourse(c)}
                  className={`p-3 rounded-xl cursor-pointer transition flex items-center justify-between border ${
                    selectedCourse?.id === c.id
                      ? 'bg-sky-500/10 border-sky-500/40 text-white'
                      : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="truncate mr-2">
                    <p className="text-sm font-semibold truncate">{c.name}</p>
                    <p className="text-xs text-slate-500">
                      {c.document_count} documents • {c.topic_count} topics
                    </p>
                  </div>
                  {selectedCourse?.id === c.id && (
                    <span className="w-2 h-2 rounded-full bg-sky-400 shrink-0" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Uploads & Document List */}
        <div className="lg:col-span-2 space-y-6">
          {selectedCourse && (
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 pb-6 border-b border-slate-800">
                <div>
                  <h2 className="text-lg font-bold text-white">{selectedCourse.name}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">{selectedCourse.description || 'No description provided'}</p>
                </div>

                <div>
                  <label className="cursor-pointer inline-flex items-center px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-sky-600/30 transition">
                    <Upload className="w-4 h-4 mr-2" />
                    {isUploading ? 'Uploading & Processing...' : 'Upload Study Notes'}
                    <input
                      type="file"
                      accept=".pdf,.txt"
                      onChange={handleFileUpload}
                      disabled={isUploading}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>

              {uploadError && (
                <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2 shrink-0" />
                  {uploadError}
                </div>
              )}

              {/* Documents List */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Uploaded Course Documents ({documents.length})
                </h3>

                {documents.length === 0 ? (
                  <div className="text-center py-12 text-slate-500 text-sm">
                    No documents uploaded yet. Upload a PDF or TXT lecture note above.
                  </div>
                ) : (
                  documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-center justify-between gap-4"
                    >
                      <div className="flex items-center min-w-0">
                        <div className="p-2.5 bg-slate-800 rounded-lg text-sky-400 mr-3 shrink-0">
                          <FileText className="w-5 h-5" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-semibold text-white truncate">{doc.original_filename}</p>
                          <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                            <span className="uppercase text-[10px] font-bold px-1.5 py-0.5 bg-slate-800 rounded text-slate-300">
                              {doc.file_type}
                            </span>
                            <span>{(doc.file_size_bytes / 1024).toFixed(1)} KB</span>
                            <span>{doc.chunk_count} chunks indexed</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        {doc.processing_status === 'completed' && (
                          <span className="inline-flex items-center text-xs font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
                            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Ready
                          </span>
                        )}
                        {doc.processing_status === 'processing' && (
                          <span className="inline-flex items-center text-xs font-medium text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-full">
                            <Clock className="w-3.5 h-3.5 mr-1 animate-spin" /> Processing
                          </span>
                        )}
                        {doc.processing_status === 'failed' && (
                          <span className="inline-flex items-center text-xs font-medium text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 rounded-full">
                            <AlertCircle className="w-3.5 h-3.5 mr-1" /> Failed
                          </span>
                        )}

                        <button
                          onClick={() => handleDeleteDocument(doc.id)}
                          className="p-2 text-slate-500 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
                          title="Delete document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
