'use client';

import { Users, Eye, PlayCircle, Activity } from 'lucide-react';
import StatCard from '@/components/StatCard';
import EngagementChart from '@/components/EngagementChart';
import TimeRangeSelector from '@/components/TimeRangeSelector';
import QuickInsights from '@/components/QuickInsights';
import CdpActivity from '@/components/CdpActivity';
import { useState, useMemo, useEffect } from 'react';
import { analyticsApi, youtubeApi } from '@/services/api';

export default function DashboardView() {
    const [timeRange, setTimeRange] = useState('7d');
    const [stats, setStats] = useState<any>(null);
    const [analyticsData, setAnalyticsData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [statsRes, analyticsRes] = await Promise.all([
                    analyticsApi.getGlobalStats(timeRange),
                    youtubeApi.getVideos()
                ]);
                setStats(statsRes.data);
                setAnalyticsData(analyticsRes.data);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [timeRange]);

    const subTrend = stats?.trends?.subscribers || { percentage_change: 0, trend: 'neutral' };
    const viewTrend = stats?.trends?.views || { percentage_change: 0, trend: 'neutral' };

    const topVideo = useMemo(() => {
        if (!Array.isArray(analyticsData?.videos) || analyticsData.videos.length === 0) return null;
        return [...analyticsData.videos].sort((a, b) => (b.views || 0) - (a.views || 0))[0];
    }, [analyticsData]);

    const insightsData = {
        top_video: topVideo ? {
            title: topVideo.title,
            views: topVideo.views,
            engagement: topVideo.views > 0 
                ? `${(((topVideo.likes + topVideo.comments) / topVideo.views) * 100).toFixed(1)}%`
                : '0%'
        } : null
    };

    return (
        <div className="animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-black text-gray-900 tracking-tight">
                        Unified Marketing Command
                    </h1>
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mt-1">
                        System Hub & Automation Control
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-lg shadow-sm">
                        <Activity className="w-4 h-4 text-orange-500" />
                        <span className="text-[10px] font-black uppercase text-gray-600">v2.5.0 Live</span>
                    </div>
                </div>
            </div>

            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard
                    title="Audience Reach"
                    value={stats?.subscriber_count?.toLocaleString() || (loading ? '...' : '0')}
                    change={`${subTrend.percentage_change > 0 ? '+' : ''}${subTrend.percentage_change}%`}
                    changeLabel="Growth Trend"
                    trend={subTrend.trend}
                    sparkline={stats?.sparklines?.subscribers || []}
                    icon={<Users className="w-6 h-6 text-orange-600" />}
                    iconBg="bg-orange-50"
                />
                <StatCard
                    title="Visual Impact"
                    value={stats?.view_count?.toLocaleString() || (loading ? '...' : '0')}
                    change={`${viewTrend.percentage_change > 0 ? '+' : ''}${viewTrend.percentage_change}%`}
                    changeLabel="Global Views"
                    trend={viewTrend.trend}
                    sparkline={stats?.sparklines?.views || []}
                    icon={<Eye className="w-6 h-6 text-green-600" />}
                    iconBg="bg-green-50"
                />
                <StatCard
                    title="Campaign Velocity"
                    value={stats?.video_count?.toLocaleString() || '0'}
                    change="Total"
                    changeLabel="Active Loops"
                    trend="neutral"
                    icon={<PlayCircle className="w-6 h-6 text-blue-600" />}
                    iconBg="bg-blue-50"
                />
            </div>

            {/* Quick Insights Section */}
            <QuickInsights data={insightsData} />

            {/* Main Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 pb-8">
                <div className="xl:col-span-2">
                     <EngagementChart data={analyticsData?.videos || []} />
                </div>
                <div className="xl:col-span-1">
                    <CdpActivity />
                </div>
            </div>
        </div>
    );
}
