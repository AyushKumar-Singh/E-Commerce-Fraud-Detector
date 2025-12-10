import { motion } from 'motion/react';
import { useState } from 'react';
import { Bell, Key, Save, Shield, Sliders } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Slider } from '../components/ui/slider';
import { Separator } from '../components/ui/separator';
import { toast } from 'sonner@2.0.3';
import { useTheme } from '../context/ThemeContext';

export function SettingsPage() {
  const { theme, toggleTheme } = useTheme();
  const [apiKey, setApiKey] = useState('sk-xxxxxxxxxxxxxxxxxxxxxxxx');
  const [fraudThreshold, setFraudThreshold] = useState([75]);
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    flaggedTransactions: true,
    fakeReviews: true,
    systemAlerts: false,
  });

  const handleSave = () => {
    toast.success('Settings saved successfully');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <h2>Settings</h2>
        <p className="text-muted-foreground">
          Configure fraud detection models, API endpoints, and system preferences
        </p>
      </motion.div>

      {/* Appearance */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>Customize the look and feel of your dashboard</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Dark Mode</Label>
                <p className="text-muted-foreground">
                  Toggle between light and dark theme
                </p>
              </div>
              <Switch checked={theme === 'dark'} onCheckedChange={toggleTheme} />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* API Configuration */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Key className="h-5 w-5 text-primary" />
              <CardTitle>API Configuration</CardTitle>
            </div>
            <CardDescription>
              Configure your backend API connection and authentication
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api-key">API Key</Label>
              <div className="flex gap-2">
                <Input
                  id="api-key"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your API key"
                  className="flex-1"
                />
                <Button variant="outline">
                  <Key className="mr-2 h-4 w-4" />
                  Generate
                </Button>
              </div>
              <p className="text-muted-foreground">
                Your API key is used to authenticate requests to the backend
              </p>
            </div>
            <Separator />
            <div className="space-y-2">
              <Label htmlFor="api-endpoint">API Endpoint</Label>
              <Input
                id="api-endpoint"
                type="url"
                placeholder="https://api.example.com"
                defaultValue="https://api.fraudshield.ai/v1"
              />
              <p className="text-muted-foreground">
                Base URL for your backend API service
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Model Configuration */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sliders className="h-5 w-5 text-primary" />
              <CardTitle>ML Model Configuration</CardTitle>
            </div>
            <CardDescription>
              Adjust Isolation Forest and NLP sentiment model parameters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Isolation Forest Settings */}
            <div className="space-y-4">
              <div>
                <p className="mb-3">Isolation Forest (Transaction Fraud)</p>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Fraud Score Threshold</Label>
                      <p className="text-muted-foreground">
                        Minimum score to flag a transaction
                      </p>
                    </div>
                    <span className="text-primary">{fraudThreshold[0]}%</span>
                  </div>
                  <Slider
                    value={fraudThreshold}
                    onValueChange={setFraudThreshold}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Anomaly Contamination</Label>
                  <p className="text-muted-foreground">
                    Expected fraud rate (0.05 = 5%)
                  </p>
                </div>
                <Input
                  type="number"
                  defaultValue="0.05"
                  step="0.01"
                  min="0"
                  max="0.5"
                  className="w-24"
                />
              </div>
            </div>

            <Separator />

            {/* NLP Sentiment Settings */}
            <div className="space-y-4">
              <div>
                <p className="mb-3">NLP Sentiment Analysis (Review Detection)</p>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Sentiment Threshold</Label>
                      <p className="text-muted-foreground">
                        Minimum authenticity score (0-1 scale)
                      </p>
                    </div>
                    <Input
                      type="number"
                      defaultValue="0.30"
                      step="0.05"
                      min="0"
                      max="1"
                      className="w-24"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Account Age Threshold</Label>
                      <p className="text-muted-foreground">
                        Flag accounts younger than (days)
                      </p>
                    </div>
                    <Input
                      type="number"
                      defaultValue="7"
                      min="1"
                      className="w-24"
                    />
                  </div>
                </div>
              </div>
            </div>

            <Separator />

            {/* Hybrid Detection */}
            <div className="space-y-3">
              <p>Hybrid Detection (AI + Rule-Based)</p>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Auto-block High Risk</Label>
                  <p className="text-muted-foreground">
                    Automatically block transactions above 90% fraud score
                  </p>
                </div>
                <Switch />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Real-time Monitoring</Label>
                  <p className="text-muted-foreground">
                    Enable continuous transaction monitoring
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Device Fingerprinting</Label>
                  <p className="text-muted-foreground">
                    Track device IDs for fraud pattern detection
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Velocity Checking</Label>
                  <p className="text-muted-foreground">
                    Monitor transaction frequency per user
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Notifications */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-primary" />
              <CardTitle>Notifications</CardTitle>
            </div>
            <CardDescription>
              Configure how and when you receive alerts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Email Notifications</Label>
                <p className="text-muted-foreground">
                  Receive alerts via email
                </p>
              </div>
              <Switch
                checked={notifications.email}
                onCheckedChange={(checked) =>
                  setNotifications({ ...notifications, email: checked })
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Push Notifications</Label>
                <p className="text-muted-foreground">
                  Receive browser push notifications
                </p>
              </div>
              <Switch
                checked={notifications.push}
                onCheckedChange={(checked) =>
                  setNotifications({ ...notifications, push: checked })
                }
              />
            </div>
            <Separator />
            <div className="space-y-4">
              <p>Alert Types</p>
              <div className="flex items-center justify-between">
                <Label>Flagged Transactions</Label>
                <Switch
                  checked={notifications.flaggedTransactions}
                  onCheckedChange={(checked) =>
                    setNotifications({ ...notifications, flaggedTransactions: checked })
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>Fake Reviews</Label>
                <Switch
                  checked={notifications.fakeReviews}
                  onCheckedChange={(checked) =>
                    setNotifications({ ...notifications, fakeReviews: checked })
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>System Alerts</Label>
                <Switch
                  checked={notifications.systemAlerts}
                  onCheckedChange={(checked) =>
                    setNotifications({ ...notifications, systemAlerts: checked })
                  }
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Security */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <CardTitle>Security</CardTitle>
            </div>
            <CardDescription>
              Manage security and privacy settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Two-Factor Authentication</Label>
                <p className="text-muted-foreground">
                  Add an extra layer of security
                </p>
              </div>
              <Switch />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Session Timeout</Label>
                <p className="text-muted-foreground">
                  Auto-logout after 30 minutes of inactivity
                </p>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="space-y-2">
              <Label>Data Retention</Label>
              <p className="text-muted-foreground">
                Transaction and review data is retained for 90 days
              </p>
              <Button variant="outline" size="sm">
                Configure
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="flex justify-end"
      >
        <Button onClick={handleSave} size="lg">
          <Save className="mr-2 h-4 w-4" />
          Save All Changes
        </Button>
      </motion.div>
    </div>
  );
}