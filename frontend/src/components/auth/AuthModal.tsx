/**
 * Auth Modal Component
 * Login/Register dialog with tabs
 */

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

// Validation schemas
const loginSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(1, 'Password is required'),
});

const registerSchema = z.object({
    username: z.string()
        .min(3, 'Username must be at least 3 characters')
        .max(20, 'Username must be at most 20 characters')
        .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
});

type LoginData = z.infer<typeof loginSchema>;
type RegisterData = z.infer<typeof registerSchema>;

interface AuthModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function AuthModal({ open, onOpenChange }: AuthModalProps) {
    const [tab, setTab] = useState<'login' | 'register'>('login');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { login, register } = useAuth();
    const { toast } = useToast();

    const loginForm = useForm<LoginData>({
        resolver: zodResolver(loginSchema),
        defaultValues: { email: '', password: '' },
    });

    const registerForm = useForm<RegisterData>({
        resolver: zodResolver(registerSchema),
        defaultValues: { username: '', email: '', password: '', confirmPassword: '' },
    });

    const handleLogin = async (data: LoginData) => {
        setIsSubmitting(true);
        try {
            await login(data);
            toast({ title: 'Welcome back!', description: 'You are now logged in.' });
            onOpenChange(false);
            loginForm.reset();
        } catch (error: unknown) {
            const err = error as { message?: string };
            toast({
                title: 'Login failed',
                description: err.message || 'Invalid email or password',
                variant: 'destructive',
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleRegister = async (data: RegisterData) => {
        setIsSubmitting(true);
        try {
            await register({
                username: data.username,
                email: data.email,
                password: data.password,
            });
            toast({ title: 'Welcome!', description: 'Your account has been created.' });
            onOpenChange(false);
            registerForm.reset();
        } catch (error: unknown) {
            const err = error as { message?: string };
            toast({
                title: 'Registration failed',
                description: err.message || 'Could not create account',
                variant: 'destructive',
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[400px] bg-background border-primary/20">
                <DialogHeader>
                    <DialogTitle className="text-center text-primary text-xl">
                        {tab === 'login' ? 'Welcome Back' : 'Create Account'}
                    </DialogTitle>
                </DialogHeader>

                <Tabs value={tab} onValueChange={(v) => setTab(v as 'login' | 'register')}>
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="login">Login</TabsTrigger>
                        <TabsTrigger value="register">Register</TabsTrigger>
                    </TabsList>

                    <TabsContent value="login" className="space-y-4 mt-4">
                        <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="login-email">Email</Label>
                                <Input
                                    id="login-email"
                                    type="email"
                                    {...loginForm.register('email')}
                                    placeholder="player@example.com"
                                />
                                {loginForm.formState.errors.email && (
                                    <p className="text-destructive text-xs">{loginForm.formState.errors.email.message}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="login-password">Password</Label>
                                <Input
                                    id="login-password"
                                    type="password"
                                    {...loginForm.register('password')}
                                    placeholder="••••••••"
                                />
                                {loginForm.formState.errors.password && (
                                    <p className="text-destructive text-xs">{loginForm.formState.errors.password.message}</p>
                                )}
                            </div>

                            <Button type="submit" className="w-full" disabled={isSubmitting}>
                                {isSubmitting ? 'Logging in...' : 'Login'}
                            </Button>
                        </form>
                    </TabsContent>

                    <TabsContent value="register" className="space-y-4 mt-4">
                        <form onSubmit={registerForm.handleSubmit(handleRegister)} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="register-username">Username</Label>
                                <Input
                                    id="register-username"
                                    {...registerForm.register('username')}
                                    placeholder="pacman_player"
                                />
                                {registerForm.formState.errors.username && (
                                    <p className="text-destructive text-xs">{registerForm.formState.errors.username.message}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="register-email">Email</Label>
                                <Input
                                    id="register-email"
                                    type="email"
                                    {...registerForm.register('email')}
                                    placeholder="player@example.com"
                                />
                                {registerForm.formState.errors.email && (
                                    <p className="text-destructive text-xs">{registerForm.formState.errors.email.message}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="register-password">Password</Label>
                                <Input
                                    id="register-password"
                                    type="password"
                                    {...registerForm.register('password')}
                                    placeholder="••••••••"
                                />
                                {registerForm.formState.errors.password && (
                                    <p className="text-destructive text-xs">{registerForm.formState.errors.password.message}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="register-confirm">Confirm Password</Label>
                                <Input
                                    id="register-confirm"
                                    type="password"
                                    {...registerForm.register('confirmPassword')}
                                    placeholder="••••••••"
                                />
                                {registerForm.formState.errors.confirmPassword && (
                                    <p className="text-destructive text-xs">{registerForm.formState.errors.confirmPassword.message}</p>
                                )}
                            </div>

                            <Button type="submit" className="w-full" disabled={isSubmitting}>
                                {isSubmitting ? 'Creating account...' : 'Create Account'}
                            </Button>
                        </form>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}
