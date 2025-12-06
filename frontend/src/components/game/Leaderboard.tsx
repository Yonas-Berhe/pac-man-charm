/**
 * Leaderboard Component
 * Displays top players with their scores
 */

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getLeaderboard, LeaderboardEntry, LeaderboardResponse } from '@/lib/leaderboard';
import { Trophy, Medal, Award, Loader2 } from 'lucide-react';

interface LeaderboardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

type Period = 'all_time' | 'monthly' | 'weekly' | 'daily';

export function Leaderboard({ open, onOpenChange }: LeaderboardProps) {
    const [period, setPeriod] = useState<Period>('all_time');
    const [data, setData] = useState<LeaderboardResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!open) return;

        const fetchLeaderboard = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const result = await getLeaderboard(period, 10);
                setData(result);
            } catch {
                setError('Failed to load leaderboard');
            } finally {
                setIsLoading(false);
            }
        };

        fetchLeaderboard();
    }, [open, period]);

    const getRankIcon = (rank: number) => {
        switch (rank) {
            case 1:
                return <Trophy className="h-5 w-5 text-yellow-500" />;
            case 2:
                return <Medal className="h-5 w-5 text-gray-400" />;
            case 3:
                return <Award className="h-5 w-5 text-amber-600" />;
            default:
                return <span className="w-5 text-center text-muted-foreground">{rank}</span>;
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[450px] bg-background border-primary/20">
                <DialogHeader>
                    <DialogTitle className="text-center text-primary text-xl flex items-center justify-center gap-2">
                        <Trophy className="h-6 w-6" />
                        Leaderboard
                    </DialogTitle>
                </DialogHeader>

                <Tabs value={period} onValueChange={(v) => setPeriod(v as Period)}>
                    <TabsList className="grid w-full grid-cols-4">
                        <TabsTrigger value="all_time">All Time</TabsTrigger>
                        <TabsTrigger value="monthly">Monthly</TabsTrigger>
                        <TabsTrigger value="weekly">Weekly</TabsTrigger>
                        <TabsTrigger value="daily">Daily</TabsTrigger>
                    </TabsList>

                    <TabsContent value={period} className="mt-4">
                        {isLoading ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            </div>
                        ) : error ? (
                            <div className="text-center py-8 text-destructive">{error}</div>
                        ) : data?.entries.length === 0 ? (
                            <div className="text-center py-8 text-muted-foreground">
                                No scores yet. Be the first!
                            </div>
                        ) : (
                            <ScrollArea className="h-[300px] pr-4">
                                <div className="space-y-2">
                                    {data?.entries.map((entry: LeaderboardEntry) => (
                                        <div
                                            key={entry.user.id}
                                            className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                                        >
                                            <div className="flex items-center gap-3">
                                                {getRankIcon(entry.rank)}
                                                <div>
                                                    <p className="font-semibold">{entry.user.username}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {entry.user.games_played} games
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-bold text-primary">
                                                    {entry.score.toLocaleString()}
                                                </p>
                                                <p className="text-xs text-muted-foreground">
                                                    {new Date(entry.achievedAt).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </ScrollArea>
                        )}
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}
