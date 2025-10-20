import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers
import mysql.connector
import warnings
import io
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Alumify Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with Plotly-inspired design
st.markdown("""
<style>
    /* PRINCIPLE 1: Clear Visual Hierarchy */
    .main-header {
        font-size: 2.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
        border-bottom: 3px solid #3498DB;
        padding-bottom: 0.5rem;
    }
    
    .section-header {
        font-size: 1.4rem;
        color: #2C3E50;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        padding: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        text-align: center;
    }
    
    .subsection-header {
        font-size: 1.1rem;
        color: #34495E;
        margin: 1.5rem 0 0.5rem 0;
        font-weight: 600;
        border-left: 4px solid #3498DB;
        padding-left: 0.5rem;
    }
    
    /* PRINCIPLE 2: Strategic Use of Color - Plotly Inspired */
    .metric-card {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
        border: 1px solid #E2E8F0;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* PRINCIPLE 3: Consistent Layout & Spacing */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border: 1px solid #E8E8E8;
    }
    
    .filter-section {
        background: #F8F9FA;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid #E9ECEF;
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
  Minimize2,
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
  // Add state for activity filters
  const [activityDateFilter, setActivityDateFilter] = useState<string>('all')
  const [activityCount, setActivityCount] = useState<number>(10)
  const [activityStartDate, setActivityStartDate] = useState<string>('')
  const [activityEndDate, setActivityEndDate] = useState<string>('')
  // Add state for fullscreen iframe
  const [isFullScreen, setIsFullScreen] = useState(false)
  // Add state for survey dialog
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
    
    /* Storytelling Elements */
    .story-card {
        background: linear-gradient(135deg, #F0F4FF 0%, #E6F3FF 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #6366F1;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);

    fetchAllData()
  }, [router])

  // Add useEffect to handle ESC key to exit fullscreen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullScreen) {
        setIsFullScreen(false)
      }
}
    
    .insight-highlight {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 1px solid #F59E0B;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-style: italic;

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isFullScreen])

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
    
    .narrative-text {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #374151;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        border-left: 4px solid #10B981;
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
    
    .alert-card {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 1px solid #EF4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
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
    
    .strategic-insight {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 1px solid #22C55E;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
  }

  // Add activity filter function
  const filterActivities = (activities: any[]) => {
    let filtered = [...activities];
    
    // Apply date filters
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

    /* Plotly-inspired color scheme */
    .plotly-primary { color: #6366F1; }
    .plotly-secondary { color: #8B5CF6; }
    .plotly-success { color: #10B981; }
    .plotly-warning { color: #F59E0B; }
    .plotly-danger { color: #EF4444; }
    
    /* Navigation styling */
    .nav-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        background: #F8F9FA;
        padding: 0.5rem;
        border-radius: 12px;
        gap: 1rem;
    // Apply count limit
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
    
    .nav-button {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        border: none;
        background: transparent;
        color: #4B5563;
        text-decoration: none;
        display: inline-block;
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
    
    .nav-button:hover {
        background: #6366F1;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
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
        fetchAllData() // Refresh all data including analytics
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
    
    .nav-button.active {
        background: #6366F1;
        color: white;
        box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
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
        fetchAllData() // Refresh all data including analytics
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
    
    /* Data Explorer Styling */
    .data-table {
        font-size: 0.85rem;
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
    
    .column-header {
        font-weight: 600;
        background-color: #f0f0f0;

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
</style>
""", unsafe_allow_html=True)

class AlumifyDashboard:
    def __init__(self):
        self.connection = self.create_connection()
        if self.connection:
            self.load_data()
        else:
            st.error("Cannot connect to database. Please check your MySQL connection.")
            st.stop()
    
    def create_connection(self):
        """Create database connection"""
        try:
            conn = mysql.connector.connect(
                host='srv2050.hstgr.io',
                user='u185173985_alumify2025',
                password='Alumify..2025',
                database='u185173985_alumify2025',
                autocommit=True
            )
            return conn
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return None
    
    def refresh_data(self):
        """Refresh all data from database"""
        if self.connection:
            try:
                self.load_data()
                return True
            except Exception as e:
                st.error(f"Error refreshing data: {e}")
                return False
        return False
    
    def load_data(self):
        """Load all data from database"""
        with st.spinner('Loading live data from database...'):
            # Load users data - EXCLUDE ADMIN from the start
            self.users_df = pd.read_sql("SELECT * FROM users WHERE role != 'admin'", self.connection)
            
            # Load activity logs
            self.activity_df = pd.read_sql("SELECT * FROM activity_logs", self.connection)
            
            # Load educational background
            self.education_df = pd.read_sql("SELECT * FROM educational_background", self.connection)
            
            # Clean graduation years: remove invalid years and convert to proper integers
            if 'year_graduated' in self.education_df.columns:
                # Replace 0, 0000, and other invalid years with NaN
                self.education_df['year_graduated'] = self.education_df['year_graduated'].replace([0, '0', '0000', ''], np.nan)
                
                # Convert to numeric, coercing errors to NaN
                self.education_df['year_graduated'] = pd.to_numeric(self.education_df['year_graduated'], errors='coerce')
                
                # Filter out unrealistic years (before 1950 or after current year + 5)
                current_year = datetime.now().year
                self.education_df['year_graduated'] = self.education_df['year_graduated'].apply(
                    lambda x: x if (pd.notna(x) and 1950 <= x <= current_year + 5) else np.nan
                )
                
                # Convert to Int64 (nullable integer) to remove decimals
                self.education_df['year_graduated'] = self.education_df['year_graduated'].astype('Int64')
            
            # Load employment data
            self.employment_df = pd.read_sql("SELECT * FROM employment_data", self.connection)
            
            # Load graduate profiles
            self.profiles_df = pd.read_sql("SELECT * FROM graduate_profiles", self.connection)
            
            # Load survey responses
            self.survey_df = pd.read_sql("SELECT * FROM survey_responses", self.connection)
            
            # Load course reasons
            self.course_reasons_df = pd.read_sql("SELECT * FROM course_reasons", self.connection)
            
            # Load unemployment reasons
            self.unemployment_df = pd.read_sql("SELECT * FROM unemployment_reasons", self.connection)
            
            # Load useful competencies
            self.competencies_df = pd.read_sql("SELECT * FROM useful_competencies", self.connection)
            
            # Create merged dataset for comprehensive analysis
            self.create_merged_data()
    
    def create_merged_data(self):
        """Create comprehensive merged dataset"""
        # Merge users with profiles
        merged = self.users_df.merge(
            self.profiles_df, left_on='id', right_on='user_id', how='left', suffixes=('', '_profile')
        )
        
        # Merge with education
        merged = merged.merge(
            self.education_df, left_on='id', right_on='user_id', how='left', suffixes=('', '_edu')
        )
        
        # Merge with employment
        merged = merged.merge(
            self.employment_df, left_on='id', right_on='user_id', how='left', suffixes=('', '_emp')
        )
        
        # Merge with survey responses
        merged = merged.merge(
            self.survey_df, left_on='id', right_on='user_id', how='left', suffixes=('', '_survey')
        )
        
        # Fix decimal years by converting to integers where appropriate
        if 'year_graduated' in merged.columns:
            merged['year_graduated'] = merged['year_graduated'].fillna(0).astype(int)
            # Replace 0 with NaN to maintain data integrity
            merged['year_graduated'] = merged['year_graduated'].replace(0, np.nan)
        
        self.merged_df = merged

def create_enhanced_filters(dashboard):
    """Create enhanced filters with dynamic year range based on available data"""
    st.sidebar.markdown("### Dashboard Controls")
    
    # Refresh button with better styling
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        if st.button("Refresh Live Data", use_container_width=True):
            if dashboard.refresh_data():
                st.sidebar.success("Data refreshed!")
            else:
                st.sidebar.error("Refresh failed")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Display Filters")
    
    # Time period filter
    st.sidebar.markdown("**Time Period**")
    time_period = st.sidebar.selectbox(
        "Select Time Range:",
        ["All Time", "Last 30 Days", "Last 90 Days", "Last Year"],
        label_visibility="collapsed"
    )
    
    # Program/degree filter with search
    st.sidebar.markdown("**Academic Programs**")
    programs = ['All Programs'] + sorted(dashboard.education_df['degree'].dropna().unique().tolist())
    selected_programs = st.sidebar.multiselect(
        "Select Programs:",
        options=programs,
        default=['All Programs'],
        help="Filter by academic program",
        label_visibility="collapsed"
    )
    
    # Dynamic Graduation Year Range - ONLY SHOWS AVAILABLE YEARS
    st.sidebar.markdown("**Graduation Years**")
    
    # Get available years from the database (already cleaned in load_data)
    available_years = dashboard.education_df['year_graduated'].dropna().unique().tolist()
    
    if available_years:
        # Convert to integers and sort
        available_years = sorted([int(year) for year in available_years if pd.notna(year)])
        
        # Create year options for the slider - only available years
        year_options = available_years
        
        # Set default range (min and max of available years)
        default_min = min(available_years)
        default_max = max(available_years)
        
        # Use select_slider to only allow available years
        year_range = st.sidebar.select_slider(
            "Select Year Range:",
            options=year_options,
            value=(default_min, default_max),
            label_visibility="collapsed"
        )
    else:
        # Fallback if no years available
        current_year = datetime.now().year
        year_range = (current_year - 5, current_year)
        st.sidebar.warning("No graduation years found in database")
    
    # Demographic filters
    st.sidebar.markdown("**Demographics**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        genders = ['All'] + dashboard.profiles_df['sex'].dropna().unique().tolist()
        selected_gender = st.selectbox("Gender", genders)
    with col2:
        employment_statuses = ['All'] + dashboard.employment_df['is_employed'].dropna().unique().tolist()
        selected_employment = st.selectbox("Employment", employment_statuses)
    
    return {
        'time_period': time_period,
        'programs': selected_programs,
        'year_range': year_range,
        'gender': selected_gender,
        'employment_status': selected_employment
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

def apply_enhanced_filters(dashboard, filters):
    """Apply enhanced filters with better logic"""
    filtered_df = dashboard.merged_df.copy()
    
    # Apply program filter
    if 'All Programs' not in filters['programs'] and filters['programs']:
        filtered_df = filtered_df[filtered_df['degree'].isin(filters['programs'])]
    
    # Apply year range filter - using exact year matching from available years
    filtered_df = filtered_df[
        (filtered_df['year_graduated'] >= filters['year_range'][0]) & 
        (filtered_df['year_graduated'] <= filters['year_range'][1])
    ]
    
    # Apply gender filter
    if filters['gender'] != 'All':
        filtered_df = filtered_df[filtered_df['sex'] == filters['gender']]
    
    # Apply employment status filter
    if filters['employment_status'] != 'All':
        filtered_df = filtered_df[filtered_df['is_employed'] == filters['employment_status']]
    
    return filtered_df
  // Filter alumni based on all filters
  const filteredAlumni = alumni.filter((alumni) => {
    // Search filter (name or email)
    const matchesSearch = searchTerm 
      ? (alumni.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
         alumni.email?.toLowerCase().includes(searchTerm.toLowerCase()))
      : true;

def generate_ai_narrative(dashboard, filtered_df, filters):
    """Generate AI-assisted narrative text based on current filters and data"""
    
    # Calculate key metrics for narrative
    total_alumni = len(dashboard.users_df)
    filtered_alumni = len(filtered_df)
    employed_count = len(filtered_df[filtered_df['is_employed'] == 'Yes'])
    employment_rate = (employed_count / filtered_alumni) * 100 if filtered_alumni > 0 else 0
    
    # Program-specific metrics
    if 'All Programs' not in filters['programs'] and filters['programs']:
        program_text = f"<span class='plotly-primary'>{', '.join(filters['programs'])}</span>"
    else:
        program_text = "all programs"
    
    # Year range text
    year_start = int(filters['year_range'][0])
    year_end = int(filters['year_range'][1])
    year_text = f"from <span class='plotly-primary'>{year_start}</span> to <span class='plotly-primary'>{year_end}</span>"
    
    # Gender text
    gender_text = f"<span class='plotly-secondary'>{filters['gender']}</span>" if filters['gender'] != 'All' else "all genders"
    
    # Build the narrative
    narrative_parts = []
    
    # Main overview with corrected counts
    narrative_parts.append(f"""
    <div class='narrative-text'>
        <strong>Current Analysis:</strong> Showing <span class='plotly-primary'>{filtered_alumni}</span> of <span class='plotly-primary'>{total_alumni}</span> total alumni (excluding admin) from {program_text} 
        who graduated {year_text}. Current employment rate: <span class='plotly-success'>{employment_rate:.0f}%</span> 
        ({employed_count} employed out of {filtered_alumni} filtered alumni).
    </div>
    """)
    
    return "\n".join(narrative_parts)
    // Program filter
    const matchesProgram = programFilter === "all" 
      ? true 
      : alumni.degree === programFilter;

def create_strategic_kpi_metrics(dashboard, filtered_df):
    """Create KPI metrics following strategic design principles"""
    st.markdown('<div class="main-header">Alumify Strategic Dashboard</div>', unsafe_allow_html=True)
    
    # Calculate strategic metrics
    total_alumni = len(dashboard.users_df)
    filtered_alumni = len(filtered_df)
    employed_count = len(filtered_df[filtered_df['is_employed'] == 'Yes'])
    employment_rate = (employed_count / filtered_alumni) * 100 if filtered_alumni > 0 else 0
    
    # Survey completion based on actual survey responses
    completed_surveys = len(dashboard.survey_df[dashboard.survey_df['is_completed'] == 1])
    survey_completion_rate = (completed_surveys / total_alumni) * 100 if total_alumni > 0 else 0
    
    recent_activity = len(dashboard.activity_df)
    
    # Program diversity
    program_diversity = filtered_df['degree'].nunique()
    
    # Create metric cards with strategic color coding
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TOTAL ALUMNI</div>
            <div class="metric-value">{total_alumni}</div>
            <div class="metric-delta">{filtered_alumni} Filtered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">EMPLOYMENT RATE</div>
            <div class="metric-value">{employment_rate:.0f}%</div>
            <div class="metric-delta">{employed_count} Employed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SURVEY COMPLETION</div>
            <div class="metric-value">{survey_completion_rate:.0f}%</div>
            <div class="metric-delta">{completed_surveys} Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ACTIVITIES</div>
            <div class="metric-value">{recent_activity}</div>
            <div class="metric-delta">Total Engagements</div>
    // Graduation year filter
    const matchesYear = yearFilter === "all" 
      ? true 
      : alumni.year_graduated?.toString() === yearFilter;

    // Employment status filter
    const matchesEmployment = employmentStatusFilter === "all"
      ? true
      : (employmentStatusFilter === "yes" && alumni.is_employed === "Yes") ||
        (employmentStatusFilter === "no" && alumni.is_employed === "No") ||
        (employmentStatusFilter === "never" && alumni.is_employed === "Never Employed");

    return matchesSearch && matchesProgram && matchesYear && matchesEmployment;
  }).slice(0, limitFilter); // Apply limit after all filtering

  // Get unique programs and years for filters
  const uniquePrograms = [...new Set(alumni.map((a) => a.degree).filter(Boolean))]
  const uniqueYears = [...new Set(alumni.map((a) => a.year_graduated).filter(Boolean))].sort((a, b) => b - a)

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
</div>
        """, unsafe_allow_html=True)
      </div>
    )
  }

def create_plotly_enhanced_visualizations(dashboard, filtered_df, filters):
    """Create enhanced Plotly visualizations with better storytelling and strategic insights"""
    
    # Use Plotly's built-in color scales
    qualitative_scale = px.colors.qualitative.Plotly
    
    # Row 1: Employment Overview with Strategic Insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="subsection-header">Employment Distribution</div>', unsafe_allow_html=True)
        if not filtered_df.empty and 'is_employed' in filtered_df.columns:
            employment_data = filtered_df['is_employed'].value_counts()
            
            fig = px.pie(
                values=employment_data.values,
                names=employment_data.index,
                title="",
                color=employment_data.index,
                color_discrete_sequence=qualitative_scale
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hole=0.4,
                marker=dict(line=dict(color='white', width=2)),
                hovertemplate='<b>%{label}</b><br>%{value} alumni<br>%{percent}<extra></extra>'
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                annotations=[dict(text='Employment', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Strategic Insight for Employment Distribution
            employed_count = employment_data.get('Yes', 0)
            total_count = employment_data.sum()
            employment_rate = (employed_count / total_count * 100) if total_count > 0 else 0
  const COLORS = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">

            if employment_rate >= 70:
                st.markdown(f"""
                <div class="strategic-insight">
                    <strong>Strong Performance:</strong> {employment_rate:.0f}% employment rate exceeds targets. 
                    Focus on maintaining industry partnerships and career development programs.
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
                """, unsafe_allow_html=True)
            elif employment_rate >= 50:
                st.markdown(f"""
                <div class="insight-highlight">
                    <strong>Growth Opportunity:</strong> {employment_rate:.0f}% employment rate shows potential. 
                    Consider enhancing internship programs and alumni networking.
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
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-card">
                    <strong>Action Required:</strong> {employment_rate:.0f}% employment rate needs improvement. 
                    Review curriculum alignment with industry needs and strengthen career services.
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
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="subsection-header">Program Performance</div>', unsafe_allow_html=True)
        if not filtered_df.empty and 'degree' in filtered_df.columns:
            program_performance = filtered_df.groupby('degree').apply(
                lambda x: (x['is_employed'] == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0
            ).reset_index(name='employment_rate')
            
            if len(program_performance) > 0:
                # Round employment rates to whole numbers
                program_performance['employment_rate'] = program_performance['employment_rate'].round(0)
                
                fig = px.bar(
                    program_performance.sort_values('employment_rate', ascending=True).tail(8),
                    x='employment_rate',
                    y='degree',
                    orientation='h',
                    title="",
                    labels={'employment_rate': 'Employment Rate (%)', 'degree': 'Program'},
                    color='employment_rate',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    xaxis_title="Employment Rate (%)",
                    yaxis_title=""
                )
                fig.update_traces(
                    hovertemplate='<b>%{y}</b><br>Employment Rate: %{x}%<extra></extra>'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Strategic Insight for Program Performance
                if len(program_performance) > 1:
                    top_program = program_performance.loc[program_performance['employment_rate'].idxmax()]
                    bottom_program = program_performance.loc[program_performance['employment_rate'].idxmin()]
                    
                    if top_program['employment_rate'] - bottom_program['employment_rate'] > 20:
                        st.markdown(f"""
                        <div class="strategic-insight">
                            <strong>Program Excellence:</strong> {top_program['degree']} leads with {top_program['employment_rate']:.0f}% employment. 
                            Document and share best practices across departments.
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
              Open Dashboard in New Tab
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
            <TabsContent value="alumni" className="space-y-6">
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
                    <Select value={yearFilter} onValueChange={setYearFilter}>
                      <SelectTrigger className="w-full sm:w-48">
                        <SelectValue placeholder="Filter by Year" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Years</SelectItem>
                        {uniqueYears.map((year) => (
                          <SelectItem key={year} value={year.toString()}>
                            {year}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Select 
                      value={employmentStatusFilter}
                      onValueChange={setEmploymentStatusFilter}
                    >
                      <SelectTrigger className="w-full sm:w-48">
                        <SelectValue placeholder="Employment Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Statuses</SelectItem>
                        <SelectItem value="yes">Employed</SelectItem>
                        <SelectItem value="no">Unemployed</SelectItem>
                        <SelectItem value="never">Never Employed</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select
                      value={limitFilter.toString()}
                      onValueChange={(value) => setLimitFilter(Number(value))}
                    >
                      <SelectTrigger className="w-full sm:w-28">
                        <SelectValue placeholder="Show: 10" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="10">Show: 10</SelectItem>
                        <SelectItem value="25">Show: 25</SelectItem>
                        <SelectItem value="50">Show: 50</SelectItem>
                        <SelectItem value="100">Show: 100</SelectItem>
                        <SelectItem value="500">Show: 500</SelectItem>
                        <SelectItem value="1000">Show: All</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Alumni Table */}
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Program</TableHead>
                          <TableHead>Year</TableHead>
                          <TableHead>Employment</TableHead>
                          <TableHead>Survey</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredAlumni.map((alumni) => (
                          <TableRow key={alumni.id}>
                            <TableCell className="font-medium">{alumni.name}</TableCell>
                            <TableCell>{alumni.email}</TableCell>
                            <TableCell>{alumni.degree || "N/A"}</TableCell>
                            <TableCell>{alumni.year_graduated || "N/A"}</TableCell>
                            <TableCell>
                              <Badge
                                variant={
                                  alumni.is_employed === "Yes"
                                    ? "default"
                                    : alumni.is_employed === "No"
                                      ? "destructive"
                                      : "secondary"
                                }
                              >
                                {alumni.is_employed || "Unknown"}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge variant={alumni.survey_completed ? "default" : "secondary"}>
                                {alumni.survey_completed ? "Completed" : "Pending"}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex space-x-2">
                                <Button variant="outline" size="sm" onClick={() => handleViewProfile(alumni)}>
                                  <Eye className="h-4 w-4" />
                                </Button>
                                <Button variant="outline" size="sm" onClick={() => handleEditProfile(alumni)}>
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button variant="outline" size="sm" onClick={() => handleGenerateReport(alumni.id)}>
                                  <FileDown className="h-4 w-4" />
                                </Button>
                                <AlertDialog>
                                  <AlertDialogTrigger asChild>
                                    <Button variant="outline" size="sm">
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  </AlertDialogTrigger>
                                  <AlertDialogContent>
                                    <AlertDialogHeader>
                                      <AlertDialogTitle>Delete Alumni Profile</AlertDialogTitle>
                                      <AlertDialogDescription>
                                        Are you sure you want to delete {alumni.name}'s profile? This action cannot be
                                        undone.
                                      </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                                      <AlertDialogAction onClick={() => handleDeleteAlumni(alumni.id)}>
                                        Delete
                                      </AlertDialogAction>
                                    </AlertDialogFooter>
                                  </AlertDialogContent>
                                </AlertDialog>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="activities" className="space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div className="flex items-center">
                      <Activity className="h-5 w-5 mr-2" />
                      <CardTitle>Recent Activities</CardTitle>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
                      <Select 
                        value={activityDateFilter} 
                        onValueChange={setActivityDateFilter}
                      >
                        <SelectTrigger className="w-full sm:w-40">
                          <SelectValue placeholder="Time Period" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Time</SelectItem>
                          <SelectItem value="today">Today</SelectItem>
                          <SelectItem value="week">This Week</SelectItem>
                          <SelectItem value="month">This Month</SelectItem>
                          <SelectItem value="custom">Custom Range</SelectItem>
                        </SelectContent>
                      </Select>

                      {activityDateFilter === 'custom' && (
                        <div className="flex gap-2">
                          <Input
                            type="date"
                            value={activityStartDate}
                            onChange={(e) => setActivityStartDate(e.target.value)}
                            className="w-full sm:w-36"
                          />
                          <Input
                            type="date"
                            value={activityEndDate}
                            onChange={(e) => setActivityEndDate(e.target.value)}
                            className="w-full sm:w-36"
                          />
</div>
                        """, unsafe_allow_html=True)
    
    # Row 2: Trends and Demographics with Strategic Insights
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="subsection-header">Graduation Timeline</div>', unsafe_allow_html=True)
        if not filtered_df.empty and 'year_graduated' in filtered_df.columns:
            # Use only valid, cleaned years
            grad_data = filtered_df[['year_graduated']].dropna()
            if not grad_data.empty:
                # Ensure years are integers
                grad_data = grad_data[grad_data['year_graduated'] >= 1950]  # Additional safety check
                grad_data['year_graduated'] = grad_data['year_graduated'].astype(int)
                grad_trend = grad_data['year_graduated'].value_counts().sort_index()
                
                if len(grad_trend) > 0:
                    fig = px.area(
                        x=grad_trend.index,
                        y=grad_trend.values,
                        title="",
                        labels={'x': 'Graduation Year', 'y': 'Number of Graduates'},
                        color_discrete_sequence=[qualitative_scale[0]]
                    )
                    fig.update_layout(
                        height=350,
                        xaxis_title="Graduation Year",
                        yaxis_title="Number of Graduates"
                    )
                    fig.update_traces(
                        fill='tozeroy', 
                        line=dict(width=3),
                        hovertemplate='<b>Year: %{x}</b><br>Graduates: %{y}<extra></extra>'
                    )
                    # Ensure x-axis shows integers without decimals
                    fig.update_xaxes(tickformat='d')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Strategic Insight for Graduation Trends
                    recent_grads = grad_trend.tail(3).sum()
                    if recent_grads > grad_trend.mean():
                        st.markdown(f"""
                        <div class="strategic-insight">
                            <strong>Growing Impact:</strong> {int(recent_grads)} recent graduates in last 3 years. 
                            Strong pipeline for alumni engagement and networking opportunities.
                      )}

                      <Select
                        value={activityCount.toString()}
                        onValueChange={(value) => setActivityCount(Number(value))}
                      >
                        <SelectTrigger className="w-full sm:w-28">
                          <SelectValue placeholder="Show: 10" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="5">Show: 5</SelectItem>
                          <SelectItem value="10">Show: 10</SelectItem>
                          <SelectItem value="20">Show: 20</SelectItem>
                          <SelectItem value="50">Show: 50</SelectItem>
                          <SelectItem value="100">Show: 100</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {filterActivities(recentActivities).map((activity) => (
                      <div key={activity.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                        <div className="flex-shrink-0">
                          {activity.activity_type === "registration" && <UserPlus className="h-5 w-5 text-blue-600" />}
                          {activity.activity_type === "login" && <Users className="h-5 w-5 text-green-600" />}
                          {activity.activity_type === "survey_completed" && (
                            <CheckCircle className="h-5 w-5 text-purple-600" />
                          )}
                          {activity.activity_type === "profile_updated" && <Edit className="h-5 w-5 text-orange-600" />}
                          {activity.activity_type === "survey_started" && (
                            <FileText className="h-5 w-5 text-yellow-600" />
                          )}
                          {activity.activity_type === "survey_updated" && <Edit className="h-5 w-5 text-blue-600" />}
</div>
                        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="subsection-header">Industry Placement</div>', unsafe_allow_html=True)
        if not filtered_df.empty and 'business_line' in filtered_df.columns:
            industries = filtered_df['business_line'].value_counts().head(6)
            
            if len(industries) > 0:
                # Remove decimals from industry counts - convert to integers
                industries_clean = industries.astype(int)
                
                fig = px.bar(
                    x=industries_clean.values,
                    y=industries_clean.index,
                    orientation='h',
                    title="",
                    labels={'x': 'Number of Alumni', 'y': 'Industry'},
                    color=industries_clean.values,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(
                    height=350,
                    showlegend=False,
                    xaxis_title="Number of Alumni",
                    yaxis_title=""
                )
                # Remove decimals from x-axis and hover text
                fig.update_xaxes(tickformat='d')
                fig.update_traces(
                    hovertemplate='<b>%{y}</b><br>Alumni Count: %{x}<extra></extra>',
                    texttemplate='%{x}',
                    textposition='outside'
                )
                # Remove color bar to avoid decimal display
                fig.update_coloraxes(showscale=False)
                st.plotly_chart(fig, use_container_width=True)
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">{activity.user_name}</p>
                          <p className="text-sm text-gray-600">{activity.description}</p>
                          <div className="flex items-center mt-1 text-xs text-gray-500">
                            <Clock className="h-3 w-3 mr-1" />
                            {new Date(activity.created_at).toLocaleString()}
                          </div>
                        </div>
                        <div className="flex-shrink-0">
                          <Badge variant="secondary">
                            {activity.activity_type.replace('_', ' ')}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="employment" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Employment Rate by Graduation Year</CardTitle>
                </CardHeader>
                <CardContent>
                  <ChartContainer
                    config={{
                      employment_rate: { label: "Employment Rate (%)", color: "#10B981" },
                      total_graduates: { label: "Total Graduates", color: "#3B82F6" },
                    }}
                    className="h-[400px]"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analytics?.graduation_years || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year_graduated" />
                        <YAxis />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Bar dataKey="employment_rate" fill="#10B981" name="Employment Rate (%)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="trends" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Employment Trends Over Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <ChartContainer
                    config={{
                      employment_rate: { label: "Employment Rate (%)", color: "#3B82F6" },
                    }}
                    className="h-[400px]"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={analytics?.trends || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Line
                          type="monotone"
                          dataKey="employment_rate"
                          stroke="#3B82F6"
                          strokeWidth={2}
                          name="Employment Rate (%)"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      {/* Profile View Dialog */}
      <Dialog open={showProfileDialog} onOpenChange={setShowProfileDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Alumni Profile - {selectedAlumni?.name}</DialogTitle>
          </DialogHeader>
          {selectedAlumni && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Personal Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="font-medium">Name:</span>
                      <span>{selectedAlumni.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Email:</span>
                      <span>{selectedAlumni.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Mobile:</span>
                      <span>{selectedAlumni.mobile_number || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Civil Status:</span>
                      <span>{selectedAlumni.civil_status || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Sex:</span>
                      <span>{selectedAlumni.sex || "N/A"}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Educational Background</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="font-medium">Degree:</span>
                      <span>{selectedAlumni.degree || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Specialization:</span>
                      <span>{selectedAlumni.specialization || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">University:</span>
                      <span>{selectedAlumni.college_university || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Year Graduated:</span>
                      <span>{selectedAlumni.year_graduated || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Honors:</span>
                      <span>{selectedAlumni.honors_awards || "N/A"}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Employment Status</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="font-medium">Employed:</span>
                      <Badge
                        variant={
                          selectedAlumni.is_employed === "Yes"
                            ? "default"
                            : selectedAlumni.is_employed === "No"
                              ? "destructive"
                              : "secondary"
                        }
                      >
                        {selectedAlumni.is_employed || "Unknown"}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Occupation:</span>
                      <span>{selectedAlumni.present_occupation || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Business Line:</span>
                      <span>{selectedAlumni.business_line || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Work Location:</span>
                      <span>{selectedAlumni.place_of_work || "N/A"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Job Level:</span>
                      <span>{selectedAlumni.job_level_current || "N/A"}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Survey Status</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="font-medium">Survey Completed:</span>
                      <Badge variant={selectedAlumni.survey_completed ? "default" : "secondary"}>
                        {selectedAlumni.survey_completed ? "Yes" : "No"}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Completed Date:</span>
                      <span>
                        {selectedAlumni.survey_completed_at
                          ? new Date(selectedAlumni.survey_completed_at).toLocaleDateString()
                          : "N/A"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Registration Date:</span>
                      <span>{new Date(selectedAlumni.created_at).toLocaleDateString()}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="flex justify-end space-x-2">
                {/* New View Survey Button */}
                <Button 
                  variant="outline" 
                  onClick={() => handleViewSurvey(selectedAlumni.id)}
                  disabled={!selectedAlumni.survey_completed}
                >
                  <FileText className="h-4 w-4 mr-2" />
                  View Survey
                </Button>

                # Strategic Insight for Industry Placement
                top_industry = industries_clean.index[0]
                top_count = industries_clean.iloc[0]
                st.markdown(f"""
                <div class="strategic-insight">
                    <strong>Industry Leader:</strong> {top_industry} employs {top_count} alumni. 
                    Strengthen partnerships and recruitment opportunities in this sector.
                <Button variant="outline" onClick={() => handleGenerateReport(selectedAlumni.id)}>
                  <FileDown className="h-4 w-4 mr-2" />
                  Generate Report
                </Button>
                <Button onClick={() => setShowProfileDialog(false)}>Close</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Profile Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Alumni Profile - {selectedAlumni?.name}</DialogTitle>
          </DialogHeader>
          {selectedAlumni && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label>Name</Label>
                    <Input
                      value={selectedAlumni.name || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, name: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Email</Label>
                    <Input
                      value={selectedAlumni.email || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, email: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Mobile Number</Label>
                    <Input
                      value={selectedAlumni.mobile_number || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, mobile_number: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Civil Status</Label>
                    <Select
                      value={selectedAlumni.civil_status || ""}
                      onValueChange={(value) => setSelectedAlumni({ ...selectedAlumni, civil_status: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select civil status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Single">Single</SelectItem>
                        <SelectItem value="Married">Married</SelectItem>
                        <SelectItem value="Separated">Separated</SelectItem>
                        <SelectItem value="Widow or Widower">Widow or Widower</SelectItem>
                        <SelectItem value="Single Parent">Single Parent</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Sex</Label>
                    <Select
                      value={selectedAlumni.sex || ""}
                      onValueChange={(value) => setSelectedAlumni({ ...selectedAlumni, sex: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select sex" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Male">Male</SelectItem>
                        <SelectItem value="Female">Female</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
</div>
                """, unsafe_allow_html=True)

def create_actionable_insights(dashboard, filtered_df):
    """Create actionable insights section"""
    st.markdown('<div class="section-header">Strategic Insights & Recommendations</div>', unsafe_allow_html=True)
    
    # Calculate insights
    total_alumni = len(dashboard.users_df)
    filtered_alumni = len(filtered_df)
    employed_rate = (len(filtered_df[filtered_df['is_employed'] == 'Yes']) / filtered_alumni) * 100 if filtered_alumni > 0 else 0
    
    # Use actual survey completion data
    completed_surveys = len(dashboard.survey_df[dashboard.survey_df['is_completed'] == 1])
    survey_rate = (completed_surveys / total_alumni) * 100 if total_alumni > 0 else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance insights
        st.markdown('<div class="subsection-header">Performance Metrics</div>', unsafe_allow_html=True)
        
        if employed_rate < 50:
            st.markdown(f"""
            <div class="alert-card">
                <strong>Attention Needed:</strong> Employment rate ({employed_rate:.0f}%) is below target. 
                Consider career development programs and industry partnerships.
            </div>
            """, unsafe_allow_html=True)
        elif employed_rate < 70:
            st.markdown(f"""
            <div class="insight-highlight">
                <strong>Growth Opportunity:</strong> Employment rate at {employed_rate:.0f}% has room for improvement. 
                Focus on internship programs and career counseling.
                <div className="space-y-4">
                  <div>
                    <Label>Degree</Label>
                    <Input
                      value={selectedAlumni.degree || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, degree: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Specialization</Label>
                    <Input
                      value={selectedAlumni.specialization || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, specialization: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>College/University</Label>
                    <Input
                      value={selectedAlumni.college_university || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, college_university: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Year Graduated</Label>
                    <Input
                      type="number"
                      value={selectedAlumni.year_graduated || ""}
                      onChange={(e) =>
                        setSelectedAlumni({
                          ...selectedAlumni,
                          year_graduated: Number.parseInt(e.target.value) || null,
                        })
                      }
                    />
                  </div>
                  <div>
                    <Label>Employment Status</Label>
                    <Select
                      value={selectedAlumni.is_employed || ""}
                      onValueChange={(value) => setSelectedAlumni({ ...selectedAlumni, is_employed: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select employment status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Yes">Yes</SelectItem>
                        <SelectItem value="No">No</SelectItem>
                        <SelectItem value="Never Employed">Never Employed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {selectedAlumni.is_employed === "Yes" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Present Occupation</Label>
                    <Input
                      value={selectedAlumni.present_occupation || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, present_occupation: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Business Line</Label>
                    <Input
                      value={selectedAlumni.business_line || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, business_line: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Place of Work</Label>
                    <Input
                      value={selectedAlumni.place_of_work || ""}
                      onChange={(e) => setSelectedAlumni({ ...selectedAlumni, place_of_work: e.target.value })}
                    />
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowEditDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleUpdateProfile} disabled={editingAlumni}>
                  {editingAlumni ? (
                    <>
                      <Save className="h-4 w-4 mr-2 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Update Profile
                    </>
                  )}
                </Button>
              </div>
</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="story-card">
                <strong>Strong Performance:</strong> Employment rate at {employed_rate:.0f}% exceeds expectations. 
                Consider scaling successful initiatives to other programs.
          )}
        </DialogContent>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={showSettingsDialog} onOpenChange={setShowSettingsDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Admin Settings</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Current Password</Label>
              <Input
                type="password"
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                placeholder="Enter current password"
              />
</div>
            """, unsafe_allow_html=True)
        
        if survey_rate < 60:
            st.markdown(f"""
            <div class="alert-card">
                <strong>Engagement Opportunity:</strong> Survey completion rate ({survey_rate:.0f}%) is low. 
                Implement targeted survey reminder campaigns and incentives.
            <div>
              <Label>New Password</Label>
              <Input
                type="password"
                value={passwordData.newPassword}
                onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                placeholder="Enter new password"
              />
</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="story-card">
                <strong>Good Engagement:</strong> {survey_rate:.0f}% survey completion indicates strong alumni involvement.
                Leverage this for deeper insights and networking opportunities.
            <div>
              <Label>Confirm New Password</Label>
              <Input
                type="password"
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                placeholder="Confirm new password"
              />
</div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Program insights
        st.markdown('<div class="subsection-header">Program Analysis</div>', unsafe_allow_html=True)
        
        # Top programs by employment
        program_employment = filtered_df.groupby('degree').apply(
            lambda x: (x['is_employed'] == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0
        ).sort_values(ascending=False)
        
        if len(program_employment) > 0:
            top_program = program_employment.index[0]
            top_rate = program_employment.iloc[0]
            
            st.markdown(f"""
            <div class="story-card">
                <strong>Top Performer:</strong> {top_program} program has {top_rate:.0f}% employment rate.
                Document best practices for knowledge sharing across departments.
            <div className="flex justify-end space-x-2 pt-4">
              <Button variant="outline" onClick={() => setShowSettingsDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleChangePassword}>Change Password</Button>
</div>
            """, unsafe_allow_html=True)
            
            if len(program_employment) > 1:
                bottom_program = program_employment.index[-1]
                bottom_rate = program_employment.iloc[-1]
                
                st.markdown(f"""
                <div class="alert-card">
                    <strong>Improvement Opportunity:</strong> {bottom_program} program at {bottom_rate:.0f}% employment needs support.
                    Consider curriculum review and industry alignment assessment.
                </div>
                """, unsafe_allow_html=True)
          </div>
        </DialogContent>
      </Dialog>

def create_data_explorer(dashboard, filtered_df):
    """Create enhanced Data Explorer with better field names and organization"""
    st.markdown('<div class="section-header">Data Explorer</div>', unsafe_allow_html=True)
    
    if not filtered_df.empty:
        # Data Explorer Filters - SIMPLIFIED: Removed survey status
        st.markdown("### Data Controls")
        col1, col2 = st.columns(2)
        
        with col1:
            # Record limit selector
            record_limit = st.selectbox(
                "Show Records:",
                [10, 25, 50, 100, "All"],
                index=1,
                help="Limit the number of records displayed"
            )
        
        with col2:
            # Sort options
            sort_by = st.selectbox(
                "Sort By:",
                ["Name", "Graduation Year", "Employment Status"],
                help="Sort the data table"
            )
        
        # Apply record limit
        if record_limit != "All":
            display_df = filtered_df.head(record_limit)
        else:
            display_df = filtered_df.copy()
        
        # Apply sorting
        sort_mapping = {
            "Name": "name",
            "Graduation Year": "year_graduated",
            "Employment Status": "is_employed"
        }
        if sort_by in sort_mapping:
            sort_column = sort_mapping[sort_by]
            if sort_column in display_df.columns:
                display_df = display_df.sort_values(sort_column, ascending=(sort_by != "Graduation Year"))
        
        # Show key metrics first
        total_alumni_no_admin = len(dashboard.users_df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Alumni (Excluding Admin)", total_alumni_no_admin)
        with col2:
            st.metric("Filtered Records", len(filtered_df))
        with col3:
            st.metric("Displayed Records", len(display_df))
        with col4:
            completed_count = len(dashboard.survey_df[dashboard.survey_df['is_completed'] == 1])
            st.metric("Completed Surveys", completed_count)
        
        # Create a cleaned dataframe with better field names
        display_df_clean = display_df.copy()
        
        # Remove unwanted columns
        columns_to_remove = ['google_id', 'region_of_origin', 'province', 'location_type']
        for col in columns_to_remove:
            if col in display_df_clean.columns:
                display_df_clean = display_df_clean.drop(columns=[col])
        
        # Rename columns for better readability
        column_mapping = {
            'id': 'User ID',
            'name': 'Full Name',
            'email': 'Email Address',
            'role': 'User Role',
            'privacy_accepted': 'Privacy Accepted',
            'created_at': 'Account Created',
            'updated_at': 'Last Updated',
            'permanent_address': 'Permanent Address',
            'telephone': 'Telephone',
            'mobile_number': 'Mobile Number',
            'civil_status': 'Civil Status',
            'sex': 'Gender',
            'birthday': 'Birth Date',
            'degree': 'Degree Program',
            'specialization': 'Specialization',
            'college_university': 'University',
            'year_graduated': 'Graduation Year',
            'honors_awards': 'Honors & Awards',
            'is_employed': 'Employment Status',
            'employment_status': 'Employment Type',
            'present_occupation': 'Current Occupation',
            'business_line': 'Industry',
            'place_of_work': 'Work Location',
            'is_first_job': 'First Job',
            'job_level_first': 'First Job Level',
            'job_level_current': 'Current Job Level',
            'initial_gross_monthly_earning': 'Initial Salary',
            'curriculum_relevant': 'Curriculum Relevant',
            'is_completed': 'Survey Status',
            'completed_at': 'Survey Completed At'
        }
        
        # Apply column renaming
        display_df_clean = display_df_clean.rename(columns=column_mapping)
        
        # Convert survey status from 1/0 to Completed/Not Completed
        if 'Survey Status' in display_df_clean.columns:
            display_df_clean['Survey Status'] = display_df_clean['Survey Status'].apply(
                lambda x: 'Completed' if x == 1 else 'Not Completed'
            )
        
        # Ensure graduation year displays as integer without decimals and handles invalid years
        if 'Graduation Year' in display_df_clean.columns:
            # Convert to numeric, handling errors
            display_df_clean['Graduation Year'] = pd.to_numeric(display_df_clean['Graduation Year'], errors='coerce')
            
            # Replace invalid years (too old or future) with empty string
            current_year = datetime.now().year
            display_df_clean['Graduation Year'] = display_df_clean['Graduation Year'].apply(
                lambda x: int(x) if pd.notna(x) and 1950 <= x <= current_year + 5 else ''
            )
        
        # Keep only the most relevant columns for display
        key_columns = [
            'Full Name', 'Email Address', 'Degree Program', 'Graduation Year', 
            'Gender', 'Employment Status', 'Current Occupation', 'Industry',
            'Work Location', 'Survey Status'
        ]
        
        # Filter to only include columns that exist in the dataframe
        available_columns = [col for col in key_columns if col in display_df_clean.columns]
        display_df_clean = display_df_clean[available_columns]
        
        # Data preview with better organization
        st.markdown("### Alumni Records")
        st.dataframe(display_df_clean, use_container_width=True)
        
        # Export options
        st.markdown("### Export Data")
        col1, col2 = st.columns(2)
        with col1:
            csv = display_df_clean.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"alumni_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            excel_buffer = io.BytesIO()
            display_df_clean.to_excel(excel_buffer, index=False, engine='openpyxl')
            st.download_button(
                label="Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"alumni_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("No data available with the current filters.")

def create_spa_navigation():
    """Create Single Page Application navigation without deprecated query parameters"""
    # Initialize session state for navigation
    if 'nav_section' not in st.session_state:
        st.session_state.nav_section = "Executive Overview"
    
    # Simple navigation using buttons without deprecated functions
    st.markdown("### Navigation")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Executive Overview", use_container_width=True, 
                    type="primary" if st.session_state.nav_section == "Executive Overview" else "secondary"):
            st.session_state.nav_section = "Executive Overview"
    with col2:
        if st.button("Data Explorer", use_container_width=True,
                    type="primary" if st.session_state.nav_section == "Data Explorer" else "secondary"):
            st.session_state.nav_section = "Data Explorer"
    
    st.markdown("---")
    return st.session_state.nav_section
      {/* Survey Data Dialog */}
      <Dialog open={showSurveyDialog} onOpenChange={setShowSurveyDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Survey Details - {surveyData?.user?.name}</DialogTitle>
          </DialogHeader>
          {surveyData && (
            <div className="space-y-6">
              {/* Personal Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Personal Information</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Name</Label>
                    <p className="font-medium">{surveyData.user.name}</p>
                  </div>
                  <div>
                    <Label>Email</Label>
                    <p className="font-medium">{surveyData.user.email}</p>
                  </div>
                  <div>
                    <Label>Mobile Number</Label>
                    <p className="font-medium">{surveyData.graduateProfile?.mobile_number || "N/A"}</p>
                  </div>
                  <div>
                    <Label>Civil Status</Label>
                    <p className="font-medium">{surveyData.graduateProfile?.civil_status || "N/A"}</p>
                  </div>
                </CardContent>
              </Card>

def main():
    # Initialize dashboard
    dashboard = AlumifyDashboard()
    
    # Sidebar with enhanced navigation
    st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h2>Alumify</h2>
        <p style='color: #666; font-size: 0.9rem;'>Strategic Alumni Analytics</p>
              {/* Educational Background */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Educational Background</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Degree</Label>
                    <p className="font-medium">{surveyData.educationalBackground?.degree || "N/A"}</p>
                  </div>
                  <div>
                    <Label>Specialization</Label>
                    <p className="font-medium">{surveyData.educationalBackground?.specialization || "N/A"}</p>
                  </div>
                  <div>
                    <Label>University</Label>
                    <p className="font-medium">{surveyData.educationalBackground?.college_university || "N/A"}</p>
                  </div>
                  <div>
                    <Label>Year Graduated</Label>
                    <p className="font-medium">{surveyData.educationalBackground?.year_graduated || "N/A"}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Course Reasons */}
              {surveyData.courseReasons && surveyData.courseReasons.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Reasons for Taking Course</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="list-disc list-inside space-y-1">
                      {surveyData.courseReasons.map((reason: string, index: number) => (
                        <li key={index}>{reason}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Employment Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Employment Information</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Employment Status</Label>
                    <p className="font-medium">{surveyData.employmentData?.is_employed || "N/A"}</p>
                  </div>
                  {surveyData.employmentData?.present_occupation && (
                    <div>
                      <Label>Occupation</Label>
                      <p className="font-medium">{surveyData.employmentData.present_occupation}</p>
                    </div>
                  )}
                  {surveyData.employmentData?.business_line && (
                    <div>
                      <Label>Business Line</Label>
                      <p className="font-medium">{surveyData.employmentData.business_line}</p>
                    </div>
                  )}
                  {surveyData.employmentData?.place_of_work && (
                    <div>
                      <Label>Place of Work</Label>
                      <p className="font-medium">{surveyData.employmentData.place_of_work}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Useful Competencies */}
              {surveyData.usefulCompetencies && surveyData.usefulCompetencies.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Useful Competencies</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="list-disc list-inside space-y-1">
                      {surveyData.usefulCompetencies.map((competency: string, index: number) => (
                        <li key={index}>{competency}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Curriculum Suggestions */}
              {surveyData.curriculumSuggestions && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Curriculum Suggestions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>{surveyData.curriculumSuggestions}</p>
                  </CardContent>
                </Card>
              )}

              <div className="flex justify-end">
                <Button onClick={() => setShowSurveyDialog(false)}>Close</Button>
              </div>
            </div>
          )}
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
    """, unsafe_allow_html=True)
    
    st.sidebar.success("Live Database Connected")
    st.sidebar.markdown("---")
    
    # Enhanced filters - now only for counting/showing
    st.sidebar.markdown("### Display Filters")
    filters = create_enhanced_filters(dashboard)
    
    # Apply filters
    filtered_df = apply_enhanced_filters(dashboard, filters)
    
    # Clean Navigation without deprecated functions
    selected_nav = create_spa_navigation()
    
    # Display AI-generated narrative (appears on all pages)
    narrative = generate_ai_narrative(dashboard, filtered_df, filters)
    st.markdown(narrative, unsafe_allow_html=True)
    
    # Display selected section
    if selected_nav == "Executive Overview":
        create_strategic_kpi_metrics(dashboard, filtered_df)
        create_plotly_enhanced_visualizations(dashboard, filtered_df, filters)
        create_actionable_insights(dashboard, filtered_df)
        
    elif selected_nav == "Data Explorer":
        create_data_explorer(dashboard, filtered_df)
    
    # Footer with data quality info
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **Data Quality:**
    - {} Total Alumni
    - {} Employment Records  
    - {} Completed Surveys
    - Updated: {}
    """.format(
        len(dashboard.users_df),
        len(dashboard.employment_df),
        len(dashboard.survey_df[dashboard.survey_df['is_completed'] == 1]),
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

if __name__ == "__main__":
    main()
  )
}
