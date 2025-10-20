import { type NextRequest, NextResponse } from "next/server"
import jwt from "jsonwebtoken"
import mysql from "mysql2/promise"
export const dynamic = "force-dynamic";

const dbConfig = {
  host: process.env.DB_HOST || "srv2050.hstgr.io",
  user: process.env.DB_USER || "u185173985_alumify2025",
  password: process.env.DB_PASSWORD || "Alumify..2025",
  database: process.env.DB_NAME || "u185173985_alumify2025",
}

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("authorization")
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 })
    }

    const token = authHeader.substring(7)
    const decoded = jwt.verify(token, process.env.JWT_SECRET || "your-secret-key") as any

    const connection = await mysql.createConnection(dbConfig)

    try {
      const [rows] = await connection.execute("SELECT privacy_accepted, privacy_accepted_at FROM users WHERE id = ?", [
        decoded.userId,
      ])

      if ((rows as any[]).length === 0) {
        return NextResponse.json({ message: "User not found" }, { status: 404 })
      }

      const user = (rows as any[])[0]

      return NextResponse.json({
        privacy_accepted: user.privacy_accepted,
        privacy_accepted_at: user.privacy_accepted_at,
      })
    } finally {
      await connection.end()
    }
  } catch (error) {
    console.error("Privacy status error:", error)
    return NextResponse.json({ message: "Internal server error" }, { status: 500 })
  }
}
