import React, { useState } from 'react';
import { Share2, Image as ImageIcon, Video, Send, Loader2, Facebook, Instagram, AlertCircle, CheckCircle2, Upload } from 'lucide-react';
import { uploadsApi, publishApi } from '@/services/api';

interface PublishResult {
  success: boolean;
  message: string;
  post_id?: string;
}

export default function SocialPublishView() {
  const [platform, setPlatform] = useState<'facebook' | 'instagram'>('facebook');
  const [content, setContent] = useState('');
  const [mediaUrl, setMediaUrl] = useState('');
  const [mediaType, setMediaType] = useState<'IMAGE' | 'REELS'>('IMAGE');
  const [isPublishing, setIsPublishing] = useState(false);
  const [result, setResult] = useState<PublishResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setMediaUrl(file.name); // Use filename as placeholder or reference
      
      // Auto-set media type based on file extension
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (['mp4', 'mov'].includes(ext || '')) {
        setMediaType('REELS');
      } else {
        setMediaType('IMAGE');
      }
    }
  };

  const handlePublish = async () => {
    if (!content && !mediaUrl && !selectedFile) {
      setResult({ success: false, message: 'Please provide content and media (URL or File).' });
      return;
    }

    setIsPublishing(true);
    setResult(null);

    try {
      let finalMediaUrl = mediaUrl;

      // 1. Upload file if selected
      if (selectedFile) {
        const uploadRes = await uploadsApi.upload(selectedFile);
        const uploadData = uploadRes.data;
        if (!uploadData.success) {
          throw new Error(uploadData.detail || 'File upload failed');
        }
        finalMediaUrl = uploadData.filename; // Send the filename to the publish endpoint
      }

      // 2. Publish
      const response = await publishApi.social({
        platform,
        content,
        media_url: finalMediaUrl || null,
        media_type: platform === 'instagram' ? mediaType : undefined,
      });

      const data = response.data;
      if (data.success) {
        setResult({
          success: true,
          message: 'Published successfully!',
          post_id: data.post_id
        });
        // Clear form on success
        setContent('');
        setMediaUrl('');
        setSelectedFile(null);
        setPreviewUrl(null);
      } else {
        setResult({
          success: false,
          message: data.error || 'Failed to publish. Please check your integration settings.'
        });
      }
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || error.response?.data?.error || error.message || 'An error occurred during publishing.'
      });
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Share2 className="w-6 h-6 text-orange-600" />
          Social Publish
        </h1>
        <p className="text-gray-500 mt-1">Create and publish content across your social channels.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Form Column */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="space-y-6">
              {/* Platform Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Select Platform</label>
                <div className="flex gap-4">
                  <button
                    onClick={() => setPlatform('facebook')}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all ${
                      platform === 'facebook'
                        ? 'border-blue-600 bg-blue-50 text-blue-600'
                        : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                    }`}
                  >
                    <Facebook className="w-5 h-5" />
                    <span className="font-semibold">Facebook</span>
                  </button>
                  <button
                    onClick={() => setPlatform('instagram')}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all ${
                      platform === 'instagram'
                        ? 'border-pink-600 bg-pink-50 text-pink-600'
                        : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                    }`}
                  >
                    <Instagram className="w-5 h-5" />
                    <span className="font-semibold">Instagram</span>
                  </button>
                </div>
              </div>

              {/* Content Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Post Content</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder={platform === 'instagram' ? "Write a caption..." : "What's on your mind?"}
                  className="w-full h-32 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all resize-none"
                />
              </div>

              {/* Media Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Media</label>
                <div className="space-y-4">
                  {/* File Upload Area */}
                  <div className="flex items-center justify-center w-full">
                    <label className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                      selectedFile ? 'border-orange-500 bg-orange-50' : 'border-gray-200 bg-gray-50 hover:bg-gray-100'
                    }`}>
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        {selectedFile ? (
                          <>
                            <CheckCircle2 className="w-8 h-8 mb-3 text-orange-500" />
                            <p className="text-sm text-orange-600 font-medium">{selectedFile.name}</p>
                          </>
                        ) : (
                          <>
                            <Upload className="w-8 h-8 mb-3 text-gray-400" />
                            <p className="text-sm text-gray-500"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                            <p className="text-xs text-gray-400">Images or Videos (max 100MB)</p>
                          </>
                        )}
                      </div>
                      <input type="file" className="hidden" onChange={handleFileChange} accept="image/*,video/*" />
                    </label>
                  </div>

                  <div className="relative flex items-center gap-3">
                    <div className="flex-1 h-px bg-gray-100"></div>
                    <span className="text-[10px] font-bold text-gray-300 uppercase">Or provide URL</span>
                    <div className="flex-1 h-px bg-gray-100"></div>
                  </div>

                  {/* URL Input */}
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <ImageIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="text"
                      value={mediaUrl}
                      onChange={(e) => {
                        setMediaUrl(e.target.value);
                        if (selectedFile) setSelectedFile(null);
                        if (previewUrl) setPreviewUrl(null);
                      }}
                      placeholder="https://example.com/image.jpg"
                      className="block w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                    />
                  </div>
                </div>
                {platform === 'instagram' && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Media Type</label>
                    <div className="flex gap-2">
                      {(['IMAGE', 'REELS'] as const).map((type) => (
                        <button
                          key={type}
                          onClick={() => setMediaType(type)}
                          className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                            mediaType === type
                              ? 'bg-orange-100 border-orange-200 text-orange-600'
                              : 'bg-gray-50 border-gray-100 text-gray-500 hover:bg-gray-100'
                          }`}
                        >
                          {type}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Status Message */}
              {result && (
                <div className={`p-4 rounded-lg flex items-start gap-3 ${
                  result.success ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'
                }`}>
                  {result.success ? <CheckCircle2 className="w-5 h-5 mt-0.5" /> : <AlertCircle className="w-5 h-5 mt-0.5" />}
                  <div>
                    <p className="text-sm font-medium">{result.message}</p>
                    {result.post_id && <p className="text-xs mt-1 opacity-70">Post ID: {result.post_id}</p>}
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                onClick={handlePublish}
                disabled={isPublishing || (platform === 'instagram' && !mediaUrl && !selectedFile)}
                className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 font-bold text-white transition-all shadow-lg ${
                  isPublishing || (platform === 'instagram' && !mediaUrl && !selectedFile)
                    ? 'bg-gray-300 cursor-not-allowed shadow-none'
                    : 'bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 active:transform active:scale-[0.98]'
                }`}
              >
                {isPublishing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Publishing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Publish Now</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Preview Column */}
        <div className="space-y-6">
          <label className="block text-sm font-medium text-gray-700">Live Preview</label>
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden max-w-[320px] mx-auto">
            {/* Social Header */}
            <div className="px-4 py-3 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-orange-500 to-yellow-500" />
              <div>
                <p className="text-xs font-bold text-gray-900">Your Business</p>
                <p className="text-[10px] text-gray-400">Sponsored • Local</p>
              </div>
            </div>

            {/* Media Area */}
            <div className="aspect-square bg-gray-50 flex items-center justify-center border-y border-gray-50">
              {previewUrl || (mediaUrl && mediaUrl.startsWith('http')) ? (
                <img src={previewUrl || mediaUrl} alt="Preview" className="w-full h-full object-cover" />
              ) : (
                <div className="flex flex-col items-center gap-2 text-gray-300">
                  {mediaType === 'REELS' ? <Video className="w-12 h-12" /> : <ImageIcon className="w-12 h-12" />}
                  <span className="text-[10px] font-medium">Media Preview</span>
                </div>
              )}
            </div>

            {/* Engagement Bar */}
            <div className="p-4 space-y-3">
              <div className="flex gap-4">
                <div className="w-5 h-5 rounded bg-gray-100" />
                <div className="w-5 h-5 rounded bg-gray-100" />
                <div className="w-5 h-5 rounded bg-gray-100 ml-auto" />
              </div>
              <div className="space-y-2">
                <div className="h-2 w-24 bg-gray-100 rounded" />
                <p className="text-xs text-gray-600 line-clamp-3 leading-relaxed">
                  <span className="font-bold text-gray-900 mr-2">Your Business</span>
                  {content || "Your post content will appear here..."}
                </p>
              </div>
              <p className="text-[10px] text-gray-300 uppercase font-medium">Just now</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
