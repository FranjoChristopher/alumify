"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { toast } from "@/hooks/use-toast"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Users,
  FileText,
  TrendingUp,
  BarChart3,
  LogOut,
  Download,
  RefreshCw,
  Search,
  Eye,
  Edit,
  Trash2,
  FileDown,
  Activity,
  Clock,
  UserPlus,
  CheckCircle,
  Settings,
  Save,
  Maximize2,
} from "lucide-react"
import { useRouter } from "next/navigation"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts"

export default function AdminDashboard() {
  const [limitFilter, setLimitFilter] = useState<number>(10)
  const [employmentStatusFilter, setEmploymentStatusFilter] = useState<string>("all")
  const [analytics, setAnalytics] = useState<any>(null)
  const [alumni, setAlumni] = useState<any[]>([])
  const [recentActivities, setRecentActivities] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [programFilter, setProgramFilter] = useState("all")
  const [yearFilter, setYearFilter] = useState("all")
  const [selectedAlumni, setSelectedAlumni] = useState<any>(null)
  const [showProfileDialog, setShowProfileDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [showSettingsDialog, setShowSettingsDialog] = useState(false)
  const [editingAlumni, setEditingAlumni] = useState(false)
  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })
  const [activityDateFilter, setActivityDateFilter] = useState<string>('all')
  const [activityCount, setActivityCount] = useState<number>(10)
  const [activityStartDate, setActivityStartDate] = useState<string>('')
  const [activityEndDate, setActivityEndDate] = useState<string>('')
  const [showSurveyDialog, setShowSurveyDialog] = useState(false)
  const [surveyData, setSurveyData] = useState<any>(null)
  
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("token")
    const userRole = localStorage.getItem("userRole")

    if (!token || userRole !== "admin") {
      router.push("/")
      return
    }

    fetchAllData()
  }, [router])

  const fetchAllData = async () => {
    setRefreshing(true)
    await Promise.all([fetchAnalytics(), fetchAlumni(), fetchRecentActivities()])
    setRefreshing(false)
    setLoading(false)
  }

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/admin/analytics", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (error) {
      console.error("Error fetching analytics:", error)
    }
  }

  const fetchAlumni = async () => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/admin/alumni", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setAlumni(data)
      }
    } catch (error) {
      console.error("Error fetching alumni:", error)
    }
  }

  const fetchRecentActivities = async () => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/admin/recent-activities", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setRecentActivities(data)
      }
    } catch (error) {
      console.error("Error fetching recent activities:", error)
    }
  }

  const filterActivities = (activities: any[]) => {
    let filtered = [...activities];
    
    if (activityDateFilter !== 'all') {
      const now = new Date();
      let startDate = new Date();
      
      switch (activityDateFilter) {
        case 'today':
          startDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          startDate.setDate(startDate.getDate() - 7);
          break;
        case 'month':
          startDate.setMonth(startDate.getMonth() - 1);
          break;
        case 'custom':
          if (activityStartDate) {
            startDate = new Date(activityStartDate);
          }
          break;
      }
      
      filtered = filtered.filter(activity => {
        const activityDate = new Date(activity.created_at);
        return activityDate >= startDate && 
              (!activityEndDate || activityDate <= new Date(activityEndDate));
      });
    }
    
    return filtered.slice(0, activityCount);
  };

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("userId")
    localStorage.removeItem("userRole")
    localStorage.removeItem("userName")
    router.push("/")
  }

  const handleExportData = async () => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/admin/export", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.style.display = "none"
        a.href = url
        a.download = "alumni_data.csv"
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        toast({
          title: "Success",
          description: "Alumni data exported successfully",
        })
      }
    } catch (error) {
      console.error("Error exporting data:", error)
      toast({
        title: "Error",
        description: "Failed to export data",
        variant: "destructive",
      })
    }
  }

  const handleGenerateReport = async (alumniId: number) => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/admin/generate-report/${alumniId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.style.display = "none"
        a.href = url
        a.download = `alumni_report_${alumniId}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        toast({
          title: "Success",
          description: "Alumni report generated successfully",
        })
      }
    } catch (error) {
      console.error("Error generating report:", error)
      toast({
        title: "Error",
        description: "Failed to generate report",
        variant: "destructive",
      })
    }
  }

  const handleDeleteAlumni = async (alumniId: number) => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/admin/alumni/${alumniId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: "Alumni profile deleted successfully",
        })
        fetchAllData()
      } else {
        const errorData = await response.json()
        toast({
          title: "Error",
          description: errorData.message || "Failed to delete alumni profile",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error deleting alumni:", error)
      toast({
        title: "Error",
        description: "Failed to delete alumni profile",
        variant: "destructive",
      })
    }
  }

  const handleViewProfile = (alumni: any) => {
    setSelectedAlumni(alumni)
    setShowProfileDialog(true)
  }

  const handleEditProfile = (alumni: any) => {
    setSelectedAlumni({ ...alumni })
    setShowEditDialog(true)
  }

  const handleUpdateProfile = async () => {
    if (!selectedAlumni) return

    setEditingAlumni(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/admin/alumni/${selectedAlumni.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(selectedAlumni),
      })

      const responseData = await response.json()

      if (response.ok) {
        toast({
          title: "Success",
          description: "Alumni profile updated successfully",
        })
        setShowEditDialog(false)
        fetchAllData()
      } else {
        toast({
          title: "Error",
          description: responseData.message || "Failed to update alumni profile",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error updating alumni:", error)
      toast({
        title: "Error",
        description: "Failed to update alumni profile",
        variant: "destructive",
      })
    } finally {
      setEditingAlumni(false)
    }
  }

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast({
        title: "Error",
        description: "New passwords do not match",
        variant: "destructive",
      })
      return
    }

    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/user/change-password", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(passwordData),
      })

      const data = await response.json()
      if (response.ok) {
        toast({
          title: "Success",
          description: "Password changed successfully",
        })
        setPasswordData({ currentPassword: "", newPassword: "", confirmPassword: "" })
        setShowSettingsDialog(false)
      } else {
        toast({
          title: "Error",
          description: data.message || "Failed to change password",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error changing password:", error)
      toast({
        title: "Error",
        description: "An error occurred while changing password",
        variant: "destructive",
      })
    }
  }

  const handleViewSurvey = async (alumniId: number) => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`/api/admin/survey/${alumniId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setSurveyData(data)
        setShowSurveyDialog(true)
      } else {
        toast({
          title: "Error",
          description: "Failed to load survey data",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching survey:", error)
      toast({
        title: "Error",
        description: "Failed to load survey data",
        variant: "destructive",
      })
    }
  }

  const filteredAlumni = alumni.filter((alumni) => {
    const matchesSearch = searchTerm 
      ? (alumni.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
         alumni.email?.toLowerCase().includes(searchTerm.toLowerCase()))
      : true;

    const matchesProgram = programFilter === "all" 
      ? true 
      : alumni.degree === programFilter;

    const matchesYear = yearFilter === "all" 
      ? true 
      : alumni.year_graduated?.toString() === yearFilter;

    const matchesEmployment = employmentStatusFilter === "all"
      ? true
      : (employmentStatusFilter === "yes" && alumni.is_employed === "Yes") ||
        (employmentStatusFilter === "no" && alumni.is_employed === "No") ||
        (employmentStatusFilter === "never" && alumni.is_employed === "Never Employed");

    return matchesSearch && matchesProgram && matchesYear && matchesEmployment;
  }).slice(0, limitFilter);

  const uniquePrograms = [...new Set(alumni.map((a) => a.degree).filter(Boolean))]
  const uniqueYears = [...new Set(alumni.map((a) => a.year_graduated).filter(Boolean))].sort((a, b) => b - a)

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    )
  }

  const COLORS = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img
                src="/alumifylogo2.png"
                alt="Alumify Logo"
                className="h-8 w-8 object-contain"
              />
              <h1 className="text-xl font-bold text-gray-900">Alumify - Admin Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={fetchAllData} disabled={refreshing}>
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
                Refresh
              </Button>
              <Button variant="outline" onClick={handleExportData}>
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
              <Button variant="ghost" onClick={() => setShowSettingsDialog(true)}>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="ghost" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Users className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Alumni</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics?.overview?.total_users || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <FileText className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Survey Responses</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics?.overview?.completed_surveys || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Employment Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics?.overview?.employment_rate || 0}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-8 w-8 text-orange-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Response Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics?.overview?.response_rate || 0}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Tabs */}
          <Tabs defaultValue="analytics" className="space-y-6">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
              <TabsTrigger value="alumni">Alumni Profiles</TabsTrigger>
              <TabsTrigger value="activities">Recent Activities</TabsTrigger>
              <TabsTrigger value="employment">Employment</TabsTrigger>
              <TabsTrigger value="trends">Trends</TabsTrigger>
            </TabsList>

            {/* Analytics Tab - Using Solution 1 */}
            <TabsContent value="analytics" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Analytics Dashboard</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <TrendingUp className="h-16 w-16 text-blue-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">Interactive Analytics</h3>
                    <p className="text-gray-600 mb-6 max-w-md mx-auto">
                      Access detailed analytics and insights through our interactive dashboard.
                    </p>
                    <div className="flex gap-4 justify-center">
                      <Button asChild>
                        <a 
                          href="https://franjochristopher-alumify-dashboard-r9n5vi.streamlit.app/" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="flex items-center gap-2"
                        >
                          <Maximize2 className="h-4 w-4" />
                          Open Dashboard
                        </a>
                      </Button>
                      <Button variant="outline" onClick={fetchAllData}>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh Data
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Rest of your tabs remain the same */}
            <TabsContent value="alumni" className="space-y-6">
              {/* Your alumni profiles content */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Alumni Profiles Management</span>
                    <Badge variant="secondary">{filteredAlumni.length} profiles</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Search and Filters */}
                  <div className="flex flex-col sm:flex-row gap-4 mb-6">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        placeholder="Search by name or email..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                    <Select value={programFilter} onValueChange={setProgramFilter}>
                      <SelectTrigger className="w-full sm:w-48">
                        <SelectValue placeholder="Filter by Program" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Programs</SelectItem>
                        {uniquePrograms.map((program) => (
                          <SelectItem key={program} value={program}>
                            {program}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {/* ... rest of your alumni table code ... */}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Other tabs (activities, employment, trends) remain the same */}
            <TabsContent value="activities" className="space-y-6">
              {/* Your activities content */}
            </TabsContent>

            <TabsContent value="employment" className="space-y-6">
              {/* Your employment content */}
            </TabsContent>

            <TabsContent value="trends" className="space-y-6">
              {/* Your trends content */}
            </TabsContent>
          </Tabs>
        </div>
      </main>

      {/* Your existing dialogs and footer */}
      {/* Profile View Dialog */}
      <Dialog open={showProfileDialog} onOpenChange={setShowProfileDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Alumni Profile - {selectedAlumni?.name}</DialogTitle>
          </DialogHeader>
          {/* ... your profile dialog content ... */}
        </DialogContent>
      </Dialog>

      {/* Edit Profile Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Alumni Profile - {selectedAlumni?.name}</DialogTitle>
          </DialogHeader>
          {/* ... your edit dialog content ... */}
        </DialogContent>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={showSettingsDialog} onOpenChange={setShowSettingsDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Admin Settings</DialogTitle>
          </DialogHeader>
          {/* ... your settings content ... */}
        </DialogContent>
      </Dialog>

      {/* Survey Data Dialog */}
      <Dialog open={showSurveyDialog} onOpenChange={setShowSurveyDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Survey Details - {surveyData?.user?.name}</DialogTitle>
          </DialogHeader>
          {/* ... your survey content ... */}
        </DialogContent>
      </Dialog>

      {/* Footer */}
      <footer className="bg-white border-t py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-500">
              &copy; {new Date().getFullYear()} Alumify
            </p>
            <div className="mt-2 md:mt-0">
              <p className="text-sm text-gray-500">
                Solution by: Alumify Team - 
                <span className="ml-2">Franjo Christopher M. Lorena,</span>
                <span className="ml-2">Carlos O. Lopez,</span>
                <span className="ml-2">Charmane M. Monis,</span>
                <span className="ml-2">Sunshine L. Tabios</span>
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
