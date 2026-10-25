import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { Course, QuizSession, QuizQuestion, QuizAnswerResult } from '../../types';
import { HelpCircle, CheckCircle2, XCircle, ArrowRight, RotateCcw, Award } from 'lucide-react';

export const QuizPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [session, setSession] = useState<QuizSession | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [answerResult, setAnswerResult] = useState<QuizAnswerResult | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [scoreSummary, setScoreSummary] = useState<{ total: number; correct: number } | null>(null);
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

  const handleStartQuiz = async () => {
    if (!selectedCourse) return;
    setLoading(true);
    try {
      const res = await api.post<QuizSession>(`/courses/${selectedCourse.id}/quizzes/sessions`, {
        question_count: 5,
      });
      setSession(res.data);
      setCurrentIdx(0);
      setSelectedOption(null);
      setAnswerResult(null);
      setIsCompleted(false);
      setScoreSummary(null);
    } catch (err: any) {
      alert(err.response?.data?.detail?.message || 'Could not start quiz session');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || selectedOption === null) return;
    const currentQ = session.questions[currentIdx];
    try {
      const res = await api.post<QuizAnswerResult>(`/quiz-sessions/${session.session_id}/answers`, {
        question_id: currentQ.id,
        selected_option_index: selectedOption,
      });
      setAnswerResult(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleNextQuestion = async () => {
    if (!session) return;
    if (currentIdx + 1 < session.questions.length) {
      setCurrentIdx(currentIdx + 1);
      setSelectedOption(null);
      setAnswerResult(null);
    } else {
      // Finalize session
      try {
        const res = await api.post(`/quiz-sessions/${session.session_id}/submit`);
        setScoreSummary({
          total: res.data.total_questions,
          correct: res.data.correct_answers,
        });
        setIsCompleted(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  if (!session) {
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-6">
        <div className="p-4 bg-sky-500/10 border border-sky-500/20 rounded-2xl w-16 h-16 flex items-center justify-center mx-auto text-sky-400">
          <HelpCircle className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Diagnostic & Practice Quiz</h1>
          <p className="text-slate-400 text-sm mt-2">
            Practice questions curated from your notes. Correct answers dynamically update your Bayesian Knowledge Tracing mastery model.
          </p>
        </div>

        <button
          onClick={handleStartQuiz}
          disabled={loading || !selectedCourse}
          className="px-8 py-3 bg-sky-600 hover:bg-sky-500 text-white font-semibold rounded-xl shadow-lg shadow-sky-600/30 transition disabled:opacity-50 cursor-pointer"
        >
          {loading ? 'Preparing Questions...' : 'Start 5-Question Quiz'}
        </button>
      </div>
    );
  }

  if (isCompleted && scoreSummary) {
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-6 bg-slate-900 border border-slate-800 rounded-3xl p-8 mt-6">
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-full w-20 h-20 flex items-center justify-center mx-auto text-emerald-400">
          <Award className="w-10 h-10" />
        </div>
        <div>
          <h2 className="text-2xl font-extrabold text-white">Quiz Session Completed!</h2>
          <p className="text-slate-400 text-sm mt-1">Your BKT learner mastery probabilities have been updated.</p>
        </div>

        <div className="p-6 bg-slate-950 rounded-2xl border border-slate-800">
          <div className="text-4xl font-extrabold text-sky-400">
            {scoreSummary.correct} / {scoreSummary.total}
          </div>
          <div className="text-sm font-semibold text-slate-400 mt-1">
            Score: {((scoreSummary.correct / scoreSummary.total) * 100).toFixed(0)}%
          </div>
        </div>

        <button
          onClick={() => setSession(null)}
          className="inline-flex items-center px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-xl transition shadow-lg shadow-sky-600/30"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Take Another Quiz
        </button>
      </div>
    );
  }

  const currentQ = session.questions[currentIdx];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Quiz Progress Header */}
      <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
        <span>Question {currentIdx + 1} of {session.total_questions}</span>
        <span className="px-2 py-0.5 bg-slate-800 rounded text-slate-300">
          Difficulty: {currentQ.difficulty}
        </span>
      </div>

      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div
          className="bg-sky-500 h-full transition-all duration-300"
          style={{ width: `${((currentIdx + 1) / session.total_questions) * 100}%` }}
        />
      </div>

      {/* Question Card */}
      <div className="bg-slate-900 border border-slate-800 p-6 md:p-8 rounded-2xl shadow-xl space-y-6">
        <h2 className="text-lg md:text-xl font-bold text-white leading-relaxed">
          {currentQ.question_text}
        </h2>

        {/* Options */}
        <div className="space-y-3">
          {currentQ.options.map((opt, i) => {
            const isSelected = selectedOption === i;
            let optionStyle = 'border-slate-800 bg-slate-950/60 hover:border-slate-700 text-slate-200';

            if (answerResult) {
              if (i === answerResult.correct_option_index) {
                optionStyle = 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300';
              } else if (isSelected && !answerResult.is_correct) {
                optionStyle = 'border-rose-500/50 bg-rose-500/10 text-rose-300';
              }
            } else if (isSelected) {
              optionStyle = 'border-sky-500 bg-sky-500/10 text-white ring-1 ring-sky-500';
            }

            return (
              <div
                key={i}
                onClick={() => {
                  if (!answerResult) setSelectedOption(i);
                }}
                className={`p-4 rounded-xl border text-sm font-medium transition cursor-pointer flex items-center justify-between ${optionStyle}`}
              >
                <span>{opt}</span>
                {answerResult && i === answerResult.correct_option_index && (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 ml-2" />
                )}
                {answerResult && isSelected && !answerResult.is_correct && (
                  <XCircle className="w-5 h-5 text-rose-400 shrink-0 ml-2" />
                )}
              </div>
            );
          })}
        </div>

        {/* Feedback & Explanation Banner */}
        {answerResult && (
          <div
            className={`p-4 rounded-xl border text-sm ${
              answerResult.is_correct
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
            }`}
          >
            <p className="font-bold mb-1">{answerResult.feedback}</p>
            {answerResult.explanation && (
              <p className="text-xs text-slate-300 mt-1">{answerResult.explanation}</p>
            )}
            <div className="mt-2 text-[11px] text-slate-400 font-mono">
              Updated BKT Mastery: {(answerResult.updated_mastery_probability * 100).toFixed(1)}%
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="flex justify-end pt-2">
          {!answerResult ? (
            <button
              onClick={handleSubmitAnswer}
              disabled={selectedOption === null}
              className="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-sm rounded-xl transition shadow-lg shadow-sky-600/30 disabled:opacity-50 cursor-pointer"
            >
              Submit Answer
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className="inline-flex items-center px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-sm rounded-xl transition shadow-lg shadow-sky-600/30 cursor-pointer"
            >
              {currentIdx + 1 < session.total_questions ? 'Next Question' : 'View Results'}
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
