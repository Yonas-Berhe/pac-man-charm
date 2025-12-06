/**
 * Game Result Dialog
 * Shows score and high score indicator after game ends
 */

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Trophy, Star, TrendingUp } from 'lucide-react';
import { GameResult } from '@/lib/games';

interface GameResultDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    result: GameResult | null;
    gameStatus: 'won' | 'lost';
    onPlayAgain: () => void;
}

export function GameResultDialog({
    open,
    onOpenChange,
    result,
    gameStatus,
    onPlayAgain,
}: GameResultDialogProps) {
    if (!result) return null;

    const isWin = gameStatus === 'won';

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[350px] bg-background border-primary/20">
                <DialogHeader>
                    <DialogTitle className={`text-center text-2xl ${isWin ? 'text-primary' : 'text-destructive'}`}>
                        {isWin ? '🎉 YOU WIN!' : '💀 GAME OVER'}
                    </DialogTitle>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    {/* Score */}
                    <div className="text-center">
                        <p className="text-muted-foreground text-sm">Final Score</p>
                        <p className="text-4xl font-bold text-primary">
                            {result.game.finalScore?.toLocaleString()}
                        </p>
                    </div>

                    {/* High Score indicator */}
                    {result.isHighScore && (
                        <div className="flex items-center justify-center gap-2 py-2 px-4 bg-yellow-500/20 rounded-lg border border-yellow-500/50">
                            <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                            <span className="font-semibold text-yellow-500">New High Score!</span>
                            <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                        </div>
                    )}

                    {/* Previous high score */}
                    {result.isHighScore && result.previousHighScore !== null && (
                        <p className="text-center text-sm text-muted-foreground">
                            Previous best: {result.previousHighScore.toLocaleString()}
                        </p>
                    )}

                    {/* Rank */}
                    {result.newRank && (
                        <div className="flex items-center justify-center gap-2 text-sm">
                            <TrendingUp className="h-4 w-4 text-green-500" />
                            <span>You ranked #{result.newRank} on the leaderboard!</span>
                        </div>
                    )}

                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-4 text-center text-sm">
                        <div className="p-2 bg-muted/50 rounded">
                            <Trophy className="h-4 w-4 mx-auto mb-1 text-primary" />
                            <p className="text-muted-foreground">Result</p>
                            <p className="font-semibold">{isWin ? 'Victory' : 'Defeat'}</p>
                        </div>
                        <div className="p-2 bg-muted/50 rounded">
                            <Star className="h-4 w-4 mx-auto mb-1 text-primary" />
                            <p className="text-muted-foreground">Status</p>
                            <p className="font-semibold">{result.isHighScore ? 'New Record' : 'Good Game'}</p>
                        </div>
                    </div>
                </div>

                <Button onClick={onPlayAgain} className="w-full">
                    {isWin ? 'Play Again' : 'Try Again'}
                </Button>
            </DialogContent>
        </Dialog>
    );
}
