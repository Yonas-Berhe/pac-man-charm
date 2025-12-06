/**
 * User Menu Component
 * Dropdown menu showing user info and logout
 */

import { useState } from 'react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { User, LogOut, Trophy } from 'lucide-react';

export function UserMenu() {
    const { user, logout } = useAuth();
    const { toast } = useToast();
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    if (!user) return null;

    const handleLogout = async () => {
        setIsLoggingOut(true);
        try {
            await logout();
            toast({ title: 'Logged out', description: 'See you next time!' });
        } catch {
            toast({
                title: 'Error',
                description: 'Failed to logout',
                variant: 'destructive',
            });
        } finally {
            setIsLoggingOut(false);
        }
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                    <User className="h-4 w-4" />
                    {user.username}
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                    <div className="flex flex-col">
                        <span className="font-semibold">{user.username}</span>
                        <span className="text-xs text-muted-foreground">{user.email}</span>
                    </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem disabled>
                    <Trophy className="mr-2 h-4 w-4" />
                    High Score: {user.high_score.toLocaleString()}
                </DropdownMenuItem>
                <DropdownMenuItem disabled>
                    <span className="ml-6 text-xs text-muted-foreground">
                        {user.games_played} games played
                    </span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} disabled={isLoggingOut}>
                    <LogOut className="mr-2 h-4 w-4" />
                    {isLoggingOut ? 'Logging out...' : 'Logout'}
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
