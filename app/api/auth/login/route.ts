import { type NextRequest, NextResponse } from "next/server"
import bcrypt from "bcryptjs"
import jwt from "jsonwebtoken"
import mysql from "mysql2/promise"

const dbConfig = {
  host: process.env.DB_HOST || "srv2050.hstgr.io",
  user: process.env.DB_USER || "u185173985_alumify2025",
  password: process.env.DB_PASSWORD || "Alumify..2025",
  database: process.env.DB_NAME || "u185173985_alumify2025",
}

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    if (!email || !password) {
      return NextResponse.json({ message: "Email and password are required" }, { status: 400 })
    }

    const connection = await mysql.createConnection(dbConfig)

    try {
      // Find user
      const [users] = await connection.execute("SELECT * FROM users WHERE email = ?", [email])

      if ((users as any[]).length === 0) {
        return NextResponse.json({ message: "Invalid credentials" }, { status: 401 })
      }

      const user = (users as any[])[0]

      // Verify password
      const isValidPassword = await bcrypt.compare(password, user.password)
      if (!isValidPassword) {
        return NextResponse.json({ message: "Invalid credentials" }, { status: 401 })
      }

      // Create JWT token
      const token = jwt.sign(
        { userId: user.id, email: user.email, role: user.role },
        process.env.JWT_SECRET || "your-secret-key",
        { expiresIn: "7d" },
      )

      // Log activity
      await connection.execute("INSERT INTO activity_logs (user_id, activity_type, description) VALUES (?, ?, ?)", [
        user.id,
        "login",
        "User logged in",
      ])

      return NextResponse.json({
        message: "Login successful",
        token,
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
          privacy_accepted: user.privacy_accepted,
        },
      })
    } finally {
      await connection.end()
    }
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json({ message: "Internal server error" }, { status: 500 })
  }
}
