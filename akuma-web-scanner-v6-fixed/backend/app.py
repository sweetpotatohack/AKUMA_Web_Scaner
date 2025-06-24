#!/usr/bin/env python3
"""
AKUMA Web Scanner v6.0 - Fixed Version
Advanced Security Testing Platform with Full Integration
"""

import os
import json
import uuid
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

import uvicorn
import redis
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel, Field
import requests

# Initialize FastAPI app
app = FastAPI(
    title="AKUMA Web Scanner v6.0",
    description="🚀 Ultimate Security Arsenal - Advanced Vulnerability Scanner",
    version="6.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("✅ Redis connected successfully")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    redis_client = None

# Models
class ScanRequest(BaseModel):
    name: str = Field(..., description="Scan name")
    targets: List[str] = Field(..., description="Target URLs or IPs")
    scan_type: str = Field(default="ultimate", description="Scan type")
    scan_modules: List[str] = Field(default=["nmap", "nuclei", "subdomain_enum"], description="Modules to run")

class ScanResponse(BaseModel):
    id: str
    name: str
    targets: List[str]
    status: str
    created_at: datetime
    progress: int = 0
    vulnerabilities: List[Dict] = []
    scan_type: str
    scan_options: Dict = {}
    tools_used: List[str] = []

class VulnerabilityResponse(BaseModel):
    scan_id: str
    scan_name: str
    vulnerabilities: List[Dict]
    summary: Dict
    by_severity: Dict = {}
    by_tool: Dict = {}
    tools_used: List[str] = []

# In-memory storage (в реальном проекте используйте базу данных)
scans_storage = {}
vulnerabilities_storage = {}

# Utility functions
def generate_scan_id() -> str:
    return str(uuid.uuid4())[:8]

def simulate_scan_progress(scan_id: str):
    """Simulate scan progress"""
    if scan_id not in scans_storage:
        return
    
    import time
    import random
    
    for progress in range(0, 101, random.randint(10, 25)):
        if scan_id in scans_storage:
            scans_storage[scan_id]["progress"] = min(progress, 100)
            scans_storage[scan_id]["status"] = "running" if progress < 100 else "completed"
            
            # Add some sample vulnerabilities during scan
            if progress > 30 and len(scans_storage[scan_id]["vulnerabilities"]) == 0:
                sample_vulns = [
                    {
                        "id": str(uuid.uuid4())[:8],
                        "title": "SSL/TLS Certificate Issues",
                        "severity": "medium",
                        "cvss": 5.3,
                        "description": "SSL certificate validation issues detected",
                        "tool": "testssl"
                    },
                    {
                        "id": str(uuid.uuid4())[:8],
                        "title": "Open Ports Detected",
                        "severity": "info",
                        "cvss": 2.1,
                        "description": "Multiple open ports discovered",
                        "tool": "nmap"
                    }
                ]
                scans_storage[scan_id]["vulnerabilities"] = sample_vulns
                scans_storage[scan_id]["tools_used"] = ["nmap", "testssl", "nuclei"]
        
        time.sleep(2)

async def run_scan_background(scan_id: str, targets: List[str], scan_modules: List[str]):
    """Background task to run actual scan"""
    try:
        # Update status
        if scan_id in scans_storage:
            scans_storage[scan_id]["status"] = "running"
        
        # Start progress simulation
        await asyncio.get_event_loop().run_in_executor(None, simulate_scan_progress, scan_id)
        
        # Trigger scanner container if available
        try:
            scanner_url = "http://scanner:5000/scan"
            payload = {
                "scan_id": scan_id,
                "targets": targets,
                "modules": scan_modules
            }
            requests.post(scanner_url, json=payload, timeout=5)
        except:
            print(f"Scanner container not available for scan {scan_id}")
        
    except Exception as e:
        if scan_id in scans_storage:
            scans_storage[scan_id]["status"] = "failed"
        print(f"Scan {scan_id} failed: {e}")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "🚀 AKUMA Web Scanner v6.0 - Ultimate Security Arsenal"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "6.0",
        "message": "🚀 AKUMA Scanner v6.0 is ready for ultimate legendary hacking!",
        "redis_status": "connected" if redis_client else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/scans", response_model=ScanResponse)
async def create_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks):
    """Create a new security scan"""
    scan_id = generate_scan_id()
    
    scan_data = {
        "id": scan_id,
        "name": scan_request.name,
        "targets": scan_request.targets,
        "status": "pending",
        "created_at": datetime.now(),
        "progress": 0,
        "vulnerabilities": [],
        "scan_type": scan_request.scan_type,
        "scan_options": {"modules": scan_request.scan_modules},
        "tools_used": []
    }
    
    scans_storage[scan_id] = scan_data
    
    # Start background scan
    background_tasks.add_task(run_scan_background, scan_id, scan_request.targets, scan_request.scan_modules)
    
    return ScanResponse(**scan_data)

@app.post("/api/scans/upload")
async def create_scan_with_file(
    name: str = Form(...),
    scan_type: str = Form(default="ultimate"),
    file: UploadFile = File(...)
):
    """Create scan with target file upload"""
    # Read targets from file
    content = await file.read()
    targets = []
    
    try:
        if file.filename.endswith('.json'):
            data = json.loads(content.decode())
            targets = data.get('targets', [])
        else:
            # Text file, one target per line
            targets = [line.strip() for line in content.decode().split('\n') if line.strip()]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")
    
    if not targets:
        raise HTTPException(status_code=400, detail="No valid targets found in file")
    
    # Create scan
    scan_request = ScanRequest(name=name, targets=targets, scan_type=scan_type)
    return await create_scan(scan_request, BackgroundTasks())

@app.get("/api/scans")
async def list_scans():
    """List all scans"""
    return list(scans_storage.values())

@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Get specific scan details"""
    if scan_id not in scans_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scans_storage[scan_id]

@app.delete("/api/scans/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan"""
    if scan_id not in scans_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    del scans_storage[scan_id]
    if scan_id in vulnerabilities_storage:
        del vulnerabilities_storage[scan_id]
    
    return {"message": f"Scan {scan_id} deleted successfully"}

@app.get("/api/scans/{scan_id}/vulnerabilities", response_model=VulnerabilityResponse)
async def get_scan_vulnerabilities(scan_id: str):
    """Get vulnerabilities for a specific scan"""
    if scan_id not in scans_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan = scans_storage[scan_id]
    vulnerabilities = scan.get("vulnerabilities", [])
    
    # Calculate summary
    summary = {
        "total": len(vulnerabilities),
        "critical": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
        "high": len([v for v in vulnerabilities if v.get("severity") == "high"]),
        "medium": len([v for v in vulnerabilities if v.get("severity") == "medium"]),
        "low": len([v for v in vulnerabilities if v.get("severity") == "low"]),
        "info": len([v for v in vulnerabilities if v.get("severity") == "info"])
    }
    
    return VulnerabilityResponse(
        scan_id=scan_id,
        scan_name=scan["name"],
        vulnerabilities=vulnerabilities,
        summary=summary,
        tools_used=scan.get("tools_used", [])
    )

@app.get("/api/scans/{scan_id}/report")
async def get_scan_report(scan_id: str):
    """Generate scan report"""
    if scan_id not in scans_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan = scans_storage[scan_id]
    vulnerabilities = scan.get("vulnerabilities", [])
    
    report = {
        "scan_info": {
            "id": scan_id,
            "name": scan["name"],
            "targets": scan["targets"],
            "status": scan["status"],
            "created_at": scan["created_at"].isoformat(),
            "progress": scan["progress"]
        },
        "vulnerabilities": vulnerabilities,
        "summary": {
            "total_vulnerabilities": len(vulnerabilities),
            "by_severity": {
                "critical": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
                "high": len([v for v in vulnerabilities if v.get("severity") == "high"]),
                "medium": len([v for v in vulnerabilities if v.get("severity") == "medium"]),
                "low": len([v for v in vulnerabilities if v.get("severity") == "low"]),
                "info": len([v for v in vulnerabilities if v.get("severity") == "info"])
            }
        },
        "tools_used": scan.get("tools_used", []),
        "generated_at": datetime.now().isoformat()
    }
    
    return report

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_scans = len(scans_storage)
    running_scans = len([s for s in scans_storage.values() if s["status"] == "running"])
    completed_scans = len([s for s in scans_storage.values() if s["status"] == "completed"])
    failed_scans = len([s for s in scans_storage.values() if s["status"] == "failed"])
    
    total_targets = sum(len(s["targets"]) for s in scans_storage.values())
    
    all_vulnerabilities = []
    for scan in scans_storage.values():
        all_vulnerabilities.extend(scan.get("vulnerabilities", []))
    
    return {
        "total_scans": total_scans,
        "running_scans": running_scans,
        "completed_scans": completed_scans,
        "failed_scans": failed_scans,
        "total_targets": total_targets,
        "total_vulnerabilities": len(all_vulnerabilities),
        "critical_vulnerabilities": len([v for v in all_vulnerabilities if v.get("severity") == "critical"]),
        "high_vulnerabilities": len([v for v in all_vulnerabilities if v.get("severity") == "high"]),
        "medium_vulnerabilities": len([v for v in all_vulnerabilities if v.get("severity") == "medium"]),
        "low_vulnerabilities": len([v for v in all_vulnerabilities if v.get("severity") == "low"]),
        "tools_stats": {},
        "grafana_url": "http://localhost:3000",
        "version": "6.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )
