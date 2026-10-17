import React, { useState } from 'react';
import { adminApi } from '../services/api';
import {
  Bell,
  Send,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Radio,
  Loader2,
  Smartphone,
  Layers,
} from 'lucide-react';

export const Notifications: React.FC = () => {
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [type, setType] = useState('SYSTEM');
  const [topic, setTopic] = useState('all');
  const [wallpaperId, setWallpaperId] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [saveToInbox, setSaveToInbox] = useState(true);

  const [isSending, setIsSending] = useState(false);
  const [isDispatchingDaily, setIsDispatchingDaily] = useState(false);
  const [resultMessage, setResultMessage] = useState<{
    success: boolean;
    text: string;
    details?: string;
  } | null>(null);

  const handleBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !message) return;

    setIsSending(true);
    setResultMessage(null);
    try {
      const payload = {
        title,
        message,
        type,
        topic: topic === 'all' ? undefined : topic,
        data: {
          if_wallpaper_id: wallpaperId ? wallpaperId : undefined,
          target_screen: wallpaperId ? 'wallpaper_details' : 'home',
          image_url: imageUrl ? imageUrl : undefined,
        },
        save_to_inbox: saveToInbox,
      };

      const resp = await adminApi.broadcastNotification(payload);
      if (resp.success && resp.data) {
        setResultMessage({
          success: true,
          text: resp.data.message,
          details: `Sent to ${resp.data.sent_count} active devices (${resp.data.delivery_mode})`,
        });
        setTitle('');
        setMessage('');
        setWallpaperId('');
        setImageUrl('');
      } else {
        setResultMessage({
          success: false,
          text: resp.message || 'Failed to dispatch broadcast',
        });
      }
    } catch (err: any) {
      setResultMessage({
        success: false,
        text: err.response?.data?.message || err.message || 'Error broadcasting push notification',
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleTriggerDaily = async () => {
    setIsDispatchingDaily(true);
    setResultMessage(null);
    try {
      const resp = await adminApi.triggerDailySpotlight();
      if (resp.success && resp.data) {
        setResultMessage({
          success: true,
          text: "Today's Daily Spotlight push alert successfully broadcasted!",
          details: `Dispatched to ${resp.data.sent_count} devices via ${resp.data.delivery_mode}`,
        });
      } else {
        setResultMessage({
          success: false,
          text: resp.message || 'Could not dispatch spotlight alert',
        });
      }
    } catch (err: any) {
      setResultMessage({
        success: false,
        text: err.response?.data?.message || err.message || 'Error triggering daily spotlight',
      });
    } finally {
      setIsDispatchingDaily(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Push & In-App Notifications</h1>
          <p className="text-xs text-slate-400 mt-1">
            Broadcast FCM push alerts, schedule daily spotlight drops, and update mobile inboxes.
          </p>
        </div>

        {/* Quick Trigger Spotlight Button */}
        <button
          onClick={handleTriggerDaily}
          disabled={isDispatchingDaily}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-purple-600 hover:from-amber-400 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/20 transition disabled:opacity-50"
        >
          {isDispatchingDaily ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
          <span>Trigger Daily Spotlight Drop</span>
        </button>
      </div>

      {/* Result Alert Banner */}
      {resultMessage && (
        <div
          className={`p-4 rounded-2xl border flex items-start gap-3 transition ${
            resultMessage.success
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
          }`}
        >
          {resultMessage.success ? (
            <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-rose-400" />
          )}
          <div>
            <p className="text-xs font-bold text-white">{resultMessage.text}</p>
            {resultMessage.details && (
              <p className="text-[11px] text-slate-400 mt-0.5 font-mono">
                {resultMessage.details}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Main Composer Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#121218] border border-[#222230]">
          <div className="flex items-center gap-2 mb-6">
            <Radio className="w-5 h-5 text-purple-400" />
            <h2 className="text-base font-bold text-white">Broadcast Push Composer</h2>
          </div>

          <form onSubmit={handleBroadcast} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                Notification Headline
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. New 8K Cyberpunk Drop! 🚀"
                className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 outline-none transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                Message Body
              </label>
              <textarea
                rows={3}
                required
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter compelling description for the push notification..."
                className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl p-3.5 text-xs text-white placeholder-slate-500 outline-none resize-none transition"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                  Notification Type
                </label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full bg-[#181822] border border-[#2B2B3D] rounded-xl px-3 py-2.5 text-xs text-white outline-none cursor-pointer"
                >
                  <option value="SYSTEM">System Announcement</option>
                  <option value="DAILY_WALLPAPER">Daily Wallpaper Spotlight</option>
                  <option value="NEW_WALLPAPER">New Wallpaper Release</option>
                  <option value="NEW_COLLECTION">New Collection Drop</option>
                  <option value="FEATURED">Featured Content</option>
                  <option value="PROMOTIONAL">Promotional</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                  Audience Topic
                </label>
                <select
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full bg-[#181822] border border-[#2B2B3D] rounded-xl px-3 py-2.5 text-xs text-white outline-none cursor-pointer"
                >
                  <option value="all">All Devices (Broadcast)</option>
                  <option value="daily_wallpaper">Daily Wallpaper Subscribers</option>
                  <option value="new_wallpapers">New Wallpaper Subscribers</option>
                  <option value="featured">Featured Subscribers</option>
                  <option value="promotional">Promotional Opt-ins</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                  Target Wallpaper ID (Optional Deep Link)
                </label>
                <input
                  type="text"
                  value={wallpaperId}
                  onChange={(e) => setWallpaperId(e.target.value)}
                  placeholder="UUID string (e.g. 550e8400-e29b-...)"
                  className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">
                  Banner Image URL (Optional Rich Push)
                </label>
                <input
                  type="url"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  placeholder="https://storage.wallpapers8k1.com/..."
                  className="w-full bg-[#181822] border border-[#2B2B3D] focus:border-purple-500 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 outline-none"
                />
              </div>
            </div>

            <div className="pt-2">
              <label className="inline-flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={saveToInbox}
                  onChange={(e) => setSaveToInbox(e.target.checked)}
                  className="w-4 h-4 accent-purple-600 rounded"
                />
                <span>Persist in user in-app notification inbox</span>
              </label>
            </div>

            <div className="pt-4 border-t border-[#222230]">
              <button
                type="submit"
                disabled={isSending}
                className="w-full py-3 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isSending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Broadcasting to FCM Network...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Dispatch Push Broadcast Now</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Info & Specs Sidecard */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#121218] border border-[#222230]">
            <div className="flex items-center gap-2 mb-4">
              <Smartphone className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white">Live Push Preview</h3>
            </div>
            <div className="p-4 rounded-xl bg-[#0B0B0E] border border-[#22222E] space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Bell className="w-3.5 h-3.5 text-purple-400" />
                  <span className="text-[10px] font-bold text-white">W8K1</span>
                </div>
                <span className="text-[9px] text-slate-500 font-mono">now</span>
              </div>
              <p className="text-xs font-semibold text-white">
                {title || 'Headline will appear here'}
              </p>
              <p className="text-[11px] text-slate-400 line-clamp-2">
                {message || 'Body message text will render on client notification shade.'}
              </p>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-[#121218] border border-[#222230]">
            <div className="flex items-center gap-2 mb-3">
              <Layers className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">FCM Delivery Architecture</h3>
            </div>
            <ul className="text-xs text-slate-400 space-y-2 leading-relaxed">
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0"></span>
                <span>FCM HTTP v1 Multicast with high-priority Android heads-up payload.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-1.5 shrink-0"></span>
                <span>Automatic token rotation and inactive device filtering.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0"></span>
                <span>Topic segmentation honoring user granular notification preferences.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
