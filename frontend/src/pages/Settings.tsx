import { fetchWithAuth } from '../utils/apiClient';
import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { Settings as SettingsIcon, User, Moon, Sun, Monitor, Bell, Shield, Mail, Lock, Check, Loader2, KeyRound } from 'lucide-react';

interface UserProfile {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: string;
  created_at: string;
  preferences: {
    theme: string;
    email_notifs: boolean;
    data_sharing: boolean;
  } | null;
}

export function Settings() {
  const { theme, setTheme } = useStore();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const [emailNotifs, setEmailNotifs] = useState(true);
  const [dataSharing, setDataSharing] = useState(false);

  // Password change state
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetchWithAuth('http://127.0.0.1:8000/api/users/me');
        if (res.ok) {
          const data: UserProfile = await res.json();
          setProfile(data);
          if (data.preferences) {
            if (data.preferences.theme) {
              setTheme(data.preferences.theme as 'light' | 'dark' | 'system');
            }
            setEmailNotifs(data.preferences.email_notifs ?? true);
            setDataSharing(data.preferences.data_sharing ?? false);
          }
        }
      } catch (err) {
        console.error("Failed to fetch profile", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const savePreferences = async (updates: { theme?: string; email_notifs?: boolean; data_sharing?: boolean }) => {
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      const res = await fetchWithAuth('http://127.0.0.1:8000/api/users/me/preferences', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (res.ok) {
        const data: UserProfile = await res.json();
        setProfile(data);
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 2000);
      }
    } catch (err) {
      console.error("Failed to save preferences", err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    savePreferences({ theme: newTheme });
  };

  const handleEmailNotifsToggle = () => {
    const newVal = !emailNotifs;
    setEmailNotifs(newVal);
    savePreferences({ email_notifs: newVal });
  };

  const handleDataSharingToggle = () => {
    const newVal = !dataSharing;
    setDataSharing(newVal);
    savePreferences({ data_sharing: newVal });
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(false);

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match");
      return;
    }
    if (newPassword.length < 6) {
      setPasswordError("Password must be at least 6 characters");
      return;
    }

    try {
      const res = await fetchWithAuth('http://127.0.0.1:8000/api/users/me/password', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to change password');
      }
      setPasswordSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setShowPasswordForm(false);
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: any) {
      setPasswordError(err.message);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <SettingsIcon className="w-8 h-8 text-primary" />
            Settings
          </h1>
          <p className="text-foreground/60 mt-1">Manage your account and application preferences.</p>
        </div>
        {isSaving && (
          <div className="flex items-center gap-2 text-sm text-primary animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            Saving...
          </div>
        )}
        {saveSuccess && (
          <div className="flex items-center gap-2 text-sm text-green-500">
            <Check className="w-4 h-4" />
            Saved!
          </div>
        )}
      </div>

      {/* ─── Profile ──────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-2">
          <div className="font-semibold text-lg flex items-center gap-2 mb-4">
            <User className="w-5 h-5 text-primary" />
            Profile
          </div>
          <p className="text-sm text-foreground/60">
            Your account information from registration.
          </p>
        </div>

        <div className="md:col-span-2 bg-card border border-border rounded-xl p-6">
          {isLoading ? (
            <div className="flex justify-center p-6">
              <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : profile ? (
            <div className="space-y-6">
              {/* Avatar + Name */}
              <div className="flex items-center gap-4 pb-4 border-b border-border">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-2xl font-bold uppercase shadow-lg shadow-primary/20">
                  {profile.username.charAt(0)}
                </div>
                <div>
                  <p className="text-xl font-semibold">{profile.username}</p>
                  <p className="text-sm text-foreground/50">{profile.email}</p>
                </div>
              </div>

              {/* Fields matching registration: Username, Email */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground/60 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5" /> Username
                  </label>
                  <div className="bg-secondary/50 border border-border rounded-xl px-4 py-3 text-foreground font-medium">
                    {profile.username}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground/60 flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5" /> Email Address
                  </label>
                  <div className="bg-secondary/50 border border-border rounded-xl px-4 py-3 text-foreground font-medium">
                    {profile.email}
                  </div>
                </div>
              </div>

              {/* Password Section */}
              <div className="pt-4 border-t border-border">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Lock className="w-4 h-4 text-foreground/60" />
                    <span className="text-sm font-medium text-foreground/80">Password</span>
                  </div>
                  <button
                    onClick={() => setShowPasswordForm(!showPasswordForm)}
                    className="text-sm text-primary hover:underline font-semibold"
                  >
                    {showPasswordForm ? 'Cancel' : 'Change Password'}
                  </button>
                </div>

                {!showPasswordForm && (
                  <div className="bg-secondary/50 border border-border rounded-xl px-4 py-3 text-foreground/50 font-medium tracking-widest text-sm">
                    ••••••••
                  </div>
                )}

                {showPasswordForm && (
                  <form onSubmit={handlePasswordChange} className="space-y-4">
                    {passwordError && (
                      <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-3 rounded-xl text-sm">
                        {passwordError}
                      </div>
                    )}
                    <div>
                      <label className="block text-sm font-medium mb-1 text-foreground/60">Current Password</label>
                      <input
                        type="password"
                        required
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="w-full bg-secondary/50 border border-border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all text-sm"
                        placeholder="Enter your current password"
                      />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1 text-foreground/60">New Password</label>
                        <input
                          type="password"
                          required
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          className="w-full bg-secondary/50 border border-border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all text-sm"
                          placeholder="••••••••"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1 text-foreground/60">Confirm New Password</label>
                        <input
                          type="password"
                          required
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          className="w-full bg-secondary/50 border border-border rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all text-sm"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>
                    <button
                      type="submit"
                      className="bg-primary hover:bg-primary/90 text-primary-foreground px-5 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-md shadow-primary/20 active:scale-[0.98]"
                    >
                      Update Password
                    </button>
                  </form>
                )}

                {passwordSuccess && (
                  <div className="bg-green-500/10 border border-green-500/20 text-green-500 p-3 rounded-xl text-sm flex items-center gap-2 mt-3">
                    <Check className="w-4 h-4" />
                    Password updated successfully!
                  </div>
                )}
              </div>
            </div>
          ) : (
            <p className="text-foreground/50">Failed to load profile.</p>
          )}
        </div>
      </div>

      <div className="w-full h-px bg-border my-8"></div>

      {/* ─── Appearance ──────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-2">
          <div className="font-semibold text-lg flex items-center gap-2 mb-4">
            <Monitor className="w-5 h-5 text-primary" />
            Appearance
          </div>
          <p className="text-sm text-foreground/60">
            Customize the look and feel of your workspace. Changes are saved automatically.
          </p>
        </div>

        <div className="md:col-span-2 bg-card border border-border rounded-xl p-6">
          <h3 className="text-sm font-medium mb-4 text-foreground/60">Theme Preference</h3>
          <div className="grid grid-cols-3 gap-4">
            <button
              onClick={() => handleThemeChange('light')}
              className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                theme === 'light' ? 'border-primary bg-primary/5 text-primary shadow-md shadow-primary/10' : 'border-border bg-card hover:bg-secondary/50 text-foreground/70'
              }`}
            >
              <Sun className="w-6 h-6 mb-2" />
              <span className="font-medium text-sm">Light</span>
            </button>
            <button
              onClick={() => handleThemeChange('dark')}
              className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                theme === 'dark' ? 'border-primary bg-primary/5 text-primary shadow-md shadow-primary/10' : 'border-border bg-card hover:bg-secondary/50 text-foreground/70'
              }`}
            >
              <Moon className="w-6 h-6 mb-2" />
              <span className="font-medium text-sm">Dark</span>
            </button>
            <button
              onClick={() => handleThemeChange('system')}
              className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                theme === 'system' ? 'border-primary bg-primary/5 text-primary shadow-md shadow-primary/10' : 'border-border bg-card hover:bg-secondary/50 text-foreground/70'
              }`}
            >
              <Monitor className="w-6 h-6 mb-2" />
              <span className="font-medium text-sm">System</span>
            </button>
          </div>
        </div>
      </div>

      <div className="w-full h-px bg-border my-8"></div>

      {/* ─── Notifications & Privacy ──────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-2">
          <div className="font-semibold text-lg flex items-center gap-2 mb-4">
            <Bell className="w-5 h-5 text-primary" />
            Notifications & Privacy
          </div>
          <p className="text-sm text-foreground/60">
            Manage your email alerts and data sharing settings. Changes are saved automatically.
          </p>
        </div>

        <div className="md:col-span-2 bg-card border border-border rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <label className="text-base font-medium">Email Notifications</label>
              <p className="text-sm text-foreground/60">Receive alerts when long-running analyses complete.</p>
            </div>
            <button 
              onClick={handleEmailNotifsToggle}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${emailNotifs ? 'bg-primary' : 'bg-secondary'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${emailNotifs ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>
          
          <div className="w-full h-px bg-border"></div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <label className="text-base font-medium flex items-center gap-2">
                Anonymous Data Sharing
                <Shield className="w-4 h-4 text-primary" />
              </label>
              <p className="text-sm text-foreground/60">Help us improve by sharing anonymous usage statistics.</p>
            </div>
            <button 
              onClick={handleDataSharingToggle}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${dataSharing ? 'bg-primary' : 'bg-secondary'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${dataSharing ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
