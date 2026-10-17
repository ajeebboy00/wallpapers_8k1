import React, { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { SearchAnalytics, SimilarWallpaperItem } from '../types';
import {
  Sparkles,
  Search,
  Palette,
  Layers,
  Cpu,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Eye,
  Sliders,
  Zap,
} from 'lucide-react';

export const AiSearch: React.FC = () => {
  const [analytics, setAnalytics] = useState<SearchAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processMessage, setProcessMessage] = useState<{
    success: boolean;
    text: string;
  } | null>(null);

  // Batch AI config
  const [batchLimit, setBatchLimit] = useState(50);
  const [forceReprocess, setForceReprocess] = useState(false);

  // Similarity inspector
  const [testWallpaperId, setTestWallpaperId] = useState('');
  const [isTestingSimilarity, setIsTestingSimilarity] = useState(false);
  const [similarResults, setSimilarResults] = useState<SimilarWallpaperItem[]>([]);
  const [testError, setTestError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const resp = await adminApi.getSearchAnalytics();
      if (resp.success && resp.data) {
        setAnalytics(resp.data);
      }
    } catch (_) {
      // Fallback
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const handleRunBatchAi = async () => {
    setIsProcessing(true);
    setProcessMessage(null);
    try {
      const resp = await adminApi.batchAiTagging({
        limit: batchLimit,
        force_reprocess: forceReprocess,
      });
      if (resp.success && resp.data) {
        setProcessMessage({
          success: true,
          text: resp.data.message || `Processed ${resp.data.processed_count} wallpapers successfully.`,
        });
        await fetchAnalytics();
      }
    } catch (err: any) {
      setProcessMessage({
        success: false,
        text: err.message || 'Failed to execute batch AI tagging pipeline.',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTestSimilarity = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testWallpaperId.trim()) return;

    setIsTestingSimilarity(true);
    setTestError(null);
    setSimilarResults([]);
    try {
      const resp = await adminApi.getSimilarWallpapers(testWallpaperId.trim(), 8);
      if (resp.success && resp.data) {
        setSimilarResults(resp.data.similar);
        if (resp.data.similar.length === 0) {
          setTestError('No similar candidates found for this wallpaper.');
        }
      }
    } catch (err: any) {
      setTestError(err.message || 'Failed to calculate visual similarity.');
    } finally {
      setIsTestingSimilarity(false);
    }
  };

  const completionPct = analytics
    ? Math.round(
        (analytics.ai_indexed_wallpapers / Math.max(1, analytics.total_wallpapers)) * 100
      )
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Sparkles className="w-7 h-7 text-purple-400" />
            AI Discovery & Visual Search Engine
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Trigram fuzzy full-text search, automated color extraction, perceptual hash, and similarity algorithms
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#1A1A22] text-slate-300 hover:text-white hover:bg-[#22222E] border border-[#22222E] transition"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-purple-400' : ''}`} />
          <span className="text-sm font-medium">Refresh Analytics</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Catalog Wallpapers</span>
            <Layers className="w-5 h-5 text-blue-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">
            {analytics ? analytics.total_wallpapers.toLocaleString() : '—'}
          </div>
          <p className="text-xs text-slate-400 mt-1">Published 8K UHD assets</p>
        </div>

        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">AI Vision Indexed</span>
            <Cpu className="w-5 h-5 text-purple-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">
            {analytics ? `${analytics.ai_indexed_wallpapers} (${completionPct}%)` : '—'}
          </div>
          <div className="mt-2 w-full bg-[#1A1A22] rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-purple-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, completionPct)}%` }}
            />
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Search Technology</span>
            <Zap className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-3 text-lg font-bold text-white">
            Postgres pg_trgm + GIN
          </div>
          <p className="text-xs text-emerald-400 mt-1">Typo-tolerant trigram search</p>
        </div>

        <div className="p-5 rounded-xl bg-[#121217] border border-[#22222E] shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Perceptual Hashing</span>
            <Sliders className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="mt-3 text-lg font-bold text-white">
            64-bit Visual Hash
          </div>
          <p className="text-xs text-slate-400 mt-1">Cosine & Hamming similarity</p>
        </div>
      </div>

      {/* Main Grid: Color Palette Visualizer & Batch Processing Console */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dominant Color Palette Visualizer */}
        <div className="p-6 rounded-xl bg-[#121217] border border-[#22222E] space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Palette className="w-5 h-5 text-purple-400" />
              Catalog Dominant Color Distribution
            </h2>
            <span className="text-xs text-slate-400">Top palette clusters</span>
          </div>

          <p className="text-xs text-slate-400">
            Automated image color extraction extracts primary hues for instantaneous color filtering in the mobile app and admin console.
          </p>

          <div className="space-y-3 pt-2">
            {analytics && analytics.color_distribution.length > 0 ? (
              analytics.color_distribution.map((item, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <div
                    className="w-7 h-7 rounded-lg border border-white/20 flex-shrink-0 shadow-sm"
                    style={{ backgroundColor: item.hex }}
                  />
                  <div className="flex-1">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-mono text-slate-300 font-semibold">{item.hex}</span>
                      <span className="text-slate-400">{item.count} items</span>
                    </div>
                    <div className="w-full bg-[#1A1A22] rounded-full h-1.5 overflow-hidden">
                      <div
                        className="h-1.5 rounded-full"
                        style={{
                          backgroundColor: item.hex,
                          width: `${Math.min(100, (item.count / Math.max(1, analytics.total_wallpapers)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">
                No color data available yet. Run the batch AI tagging pipeline below to analyze colors.
              </p>
            )}
          </div>
        </div>

        {/* Batch AI Processing Trigger */}
        <div className="p-6 rounded-xl bg-[#121217] border border-[#22222E] space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-indigo-400" />
              Automated AI Vision Tagging Pipeline
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Extracts high-resolution visual tags, assigns dominant colors, builds 5-color palettes, and generates 64-bit perceptual visual hashes.
            </p>

            <div className="mt-6 space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1.5">
                  Batch Processing Size
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[25, 50, 100].map((size) => (
                    <button
                      key={size}
                      type="button"
                      onClick={() => setBatchLimit(size)}
                      className={`py-2 px-3 text-xs font-medium rounded-lg border transition ${
                        batchLimit === size
                          ? 'bg-purple-600/20 text-purple-400 border-purple-500/50'
                          : 'bg-[#1A1A22] text-slate-400 border-[#22222E] hover:text-white'
                      }`}
                    >
                      {size} Wallpapers
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="forceReprocess"
                  checked={forceReprocess}
                  onChange={(e) => setForceReprocess(e.target.checked)}
                  className="rounded border-[#22222E] bg-[#1A1A22] text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="forceReprocess" className="text-xs text-slate-300 select-none">
                  Force re-analyze wallpapers that already possess AI tags
                </label>
              </div>

              {processMessage && (
                <div
                  className={`p-3.5 rounded-lg border text-xs flex items-center gap-2 ${
                    processMessage.success
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                      : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
                  }`}
                >
                  {processMessage.success ? (
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  )}
                  <span>{processMessage.text}</span>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={handleRunBatchAi}
            disabled={isProcessing}
            className="w-full py-3 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-purple-600/30 disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running AI Vision Analysis Pipeline...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Run Batch AI Tagging & Palette Extraction</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Visual Similarity Tester & Inspector */}
      <div className="p-6 rounded-xl bg-[#121217] border border-[#22222E] space-y-4">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Search className="w-5 h-5 text-cyan-400" />
            Visual & Semantic Similarity Inspector
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Test the multi-dimensional similarity engine by providing a source wallpaper UUID to view ranking candidates.
          </p>
        </div>

        <form onSubmit={handleTestSimilarity} className="flex gap-3">
          <input
            type="text"
            placeholder="Enter Wallpaper UUID (e.g. 550e8400-e29b-41d4-a716-446655440000)..."
            value={testWallpaperId}
            onChange={(e) => setTestWallpaperId(e.target.value)}
            className="flex-1 px-4 py-2.5 bg-[#1A1A22] border border-[#22222E] rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition"
          />
          <button
            type="submit"
            disabled={isTestingSimilarity || !testWallpaperId.trim()}
            className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm rounded-lg transition disabled:opacity-50 flex items-center gap-2"
          >
            {isTestingSimilarity ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
            <span>Calculate Similar</span>
          </button>
        </form>

        {testError && (
          <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{testError}</span>
          </div>
        )}

        {similarResults.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-3">
            {similarResults.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-[#1A1A22] border border-[#22222E] space-y-2.5 overflow-hidden"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white truncate max-w-[140px]">
                    {item.wallpaper.title}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                    {Math.round(item.similarity_score * 100)}%
                  </span>
                </div>

                <div className="flex flex-wrap gap-1">
                  {item.matching_factors.map((factor, fIdx) => (
                    <span
                      key={fIdx}
                      className="text-[10px] font-medium px-2 py-0.5 rounded bg-[#121217] text-slate-300 border border-[#22222E]"
                    >
                      {factor}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-[#22222E]/80">
                  <span>{item.wallpaper.resolution}</span>
                  <span className="font-mono text-[10px]">
                    {item.wallpaper.dominant_color || 'None'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
