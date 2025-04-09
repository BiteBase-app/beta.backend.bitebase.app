from fastapi import APIRouter, HTTPException, Query, Path, Depends, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/team", tags=["team"])

# Enums for fixed values
class UserRole(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    ANALYST = "analyst"
    MARKETING = "marketing"
    CUSTOM = "custom"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REJECTED = "rejected"

# Permission model
class Permission(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

# Team member models
class TeamMemberBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMember(TeamMemberBase):
    id: str
    avatar_url: Optional[str] = None
    permissions: List[str]
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# Invitation models
class InvitationBase(BaseModel):
    email: EmailStr
    role: UserRole
    message: Optional[str] = None

class InvitationCreate(InvitationBase):
    pass

class Invitation(InvitationBase):
    id: str
    status: InvitationStatus
    sent_by: str
    date_sent: datetime
    date_expires: datetime
    date_responded: Optional[datetime] = None

# Role models
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: str
    created_at: datetime
    updated_at: datetime
    user_count: int

# Sample data for demonstration
sample_permissions = [
    {
        "id": "view_data",
        "name": "View Data",
        "description": "Access to view data and reports"
    },
    {
        "id": "edit_data",
        "name": "Edit Data",
        "description": "Permission to edit and update data"
    },
    {
        "id": "export_reports",
        "name": "Export Reports",
        "description": "Ability to export reports and data"
    },
    {
        "id": "invite_members",
        "name": "Invite Team Members",
        "description": "Permission to invite new team members"
    },
    {
        "id": "manage_team",
        "name": "Manage Team",
        "description": "Permission to manage team members and roles"
    },
    {
        "id": "manage_billing",
        "name": "Manage Billing",
        "description": "Access to billing and subscription settings"
    },
    {
        "id": "admin",
        "name": "Full Access",
        "description": "Complete access to all features and settings"
    }
]

sample_team_members = [
    {
        "id": "1",
        "name": "John Smith",
        "email": "john.smith@example.com",
        "role": "owner",
        "status": "active",
        "avatar_url": "https://ui-avatars.com/api/?name=John+Smith&background=random",
        "permissions": ["admin", "edit_data", "view_data"],
        "last_active": datetime.now(),
        "created_at": datetime(2023, 1, 15),
        "updated_at": datetime(2023, 3, 10)
    },
    {
        "id": "2",
        "name": "Emma Johnson",
        "email": "emma.johnson@example.com",
        "role": "manager",
        "status": "active",
        "avatar_url": "https://ui-avatars.com/api/?name=Emma+Johnson&background=random",
        "permissions": ["edit_data", "view_data"],
        "last_active": datetime.now(),
        "created_at": datetime(2023, 1, 20),
        "updated_at": datetime(2023, 2, 5)
    },
    {
        "id": "3",
        "name": "Michael Williams",
        "email": "michael.williams@example.com",
        "role": "analyst",
        "status": "active",
        "avatar_url": "https://ui-avatars.com/api/?name=Michael+Williams&background=random",
        "permissions": ["view_data"],
        "last_active": datetime.now() - datetime.timedelta(days=1),
        "created_at": datetime(2023, 2, 10),
        "updated_at": datetime(2023, 2, 10)
    },
    {
        "id": "4",
        "name": "Sarah Brown",
        "email": "sarah.brown@example.com",
        "role": "marketing",
        "status": "inactive",
        "avatar_url": "https://ui-avatars.com/api/?name=Sarah+Brown&background=random",
        "permissions": ["view_data"],
        "last_active": datetime.now() - datetime.timedelta(days=14),
        "created_at": datetime(2023, 1, 25),
        "updated_at": datetime(2023, 1, 25)
    }
]

sample_invitations = [
    {
        "id": "1",
        "email": "david.jones@example.com",
        "role": "analyst",
        "message": "Hi David, we'd like you to join our team as an analyst.",
        "status": "pending",
        "sent_by": "1",  # John Smith
        "date_sent": datetime.now() - datetime.timedelta(days=3),
        "date_expires": datetime.now() + datetime.timedelta(days=4),
        "date_responded": None
    },
    {
        "id": "2",
        "email": "lisa.miller@example.com",
        "role": "marketing",
        "message": "Hi Lisa, please join our team to help with marketing insights.",
        "status": "expired",
        "sent_by": "1",  # John Smith
        "date_sent": datetime.now() - datetime.timedelta(days=10),
        "date_expires": datetime.now() - datetime.timedelta(days=3),
        "date_responded": None
    }
]

sample_roles = [
    {
        "id": "1",
        "name": "Owner",
        "description": "Full access to all features and settings",
        "permissions": ["admin", "manage_team", "manage_billing", "edit_data", "view_data"],
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime(2023, 1, 1),
        "user_count": 1
    },
    {
        "id": "2",
        "name": "Manager",
        "description": "Can edit data and manage some team settings",
        "permissions": ["edit_data", "view_data", "export_reports"],
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime(2023, 1, 1),
        "user_count": 1
    },
    {
        "id": "3",
        "name": "Analyst",
        "description": "Can view and analyze data",
        "permissions": ["view_data", "export_reports"],
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime(2023, 1, 1),
        "user_count": 1
    },
    {
        "id": "4",
        "name": "Marketing",
        "description": "Limited access focused on marketing data",
        "permissions": ["view_data"],
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime(2023, 1, 1),
        "user_count": 1
    }
]

@router.get("/members", response_model=List[TeamMember])
async def get_team_members(
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """
    Get the list of team members with filtering options.
    """
    members = sample_team_members
    
    # Apply filters
    if status:
        members = [m for m in members if m["status"] == status]
    
    if role:
        members = [m for m in members if m["role"] == role]
    
    if search:
        search = search.lower()
        members = [
            m for m in members 
            if search in m["name"].lower() or search in m["email"].lower()
        ]
    
    return members

@router.get("/members/{member_id}", response_model=TeamMember)
async def get_team_member(
    member_id: str = Path(..., description="Team member ID")
):
    """
    Get detailed information about a specific team member.
    """
    member = next((m for m in sample_team_members if m["id"] == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail=f"Team member with ID {member_id} not found")
    
    return member

@router.post("/members", response_model=TeamMember, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    member: TeamMemberCreate,
    organization_id: str = Query(..., description="Organization ID")
):
    """
    Add a new team member directly.
    """
    # In a real implementation, this would create a new user in the database
    # For demo purposes, returning a mock response
    new_id = str(len(sample_team_members) + 1)
    new_member = {
        "id": new_id,
        **member.dict(),
        "avatar_url": f"https://ui-avatars.com/api/?name={member.name.replace(' ', '+')}&background=random",
        "permissions": get_default_permissions_for_role(member.role),
        "last_active": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # In a real implementation, would add to database
    return new_member

@router.put("/members/{member_id}", response_model=TeamMember)
async def update_team_member(
    member_id: str,
    member_update: TeamMemberBase
):
    """
    Update an existing team member.
    """
    member = next((m for m in sample_team_members if m["id"] == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail=f"Team member with ID {member_id} not found")
    
    # In a real implementation, this would update the database
    # For demo purposes, just returning the updated member
    updated_member = {
        **member,
        **member_update.dict(),
        "updated_at": datetime.now()
    }
    
    return updated_member

@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    member_id: str
):
    """
    Remove a team member.
    """
    member = next((m for m in sample_team_members if m["id"] == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail=f"Team member with ID {member_id} not found")
    
    # In a real implementation, this would delete from the database or mark as removed
    return None

@router.get("/invitations", response_model=List[Invitation])
async def get_invitations(
    organization_id: Optional[str] = Query(None, description="Organization ID"),
    status: Optional[InvitationStatus] = Query(None, description="Filter by status")
):
    """
    Get the list of pending invitations.
    """
    invitations = sample_invitations
    
    if status:
        invitations = [i for i in invitations if i["status"] == status]
    
    return invitations

@router.post("/invitations", response_model=Invitation, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation: InvitationCreate,
    organization_id: str = Query(..., description="Organization ID"),
    current_user_id: str = Query(..., description="Current user ID (who is sending the invitation)")
):
    """
    Send a new team invitation.
    """
    # In a real implementation, this would create a new invitation in the database and send an email
    # For demo purposes, returning a mock response
    new_id = str(len(sample_invitations) + 1)
    new_invitation = {
        "id": new_id,
        **invitation.dict(),
        "status": "pending",
        "sent_by": current_user_id,
        "date_sent": datetime.now(),
        "date_expires": datetime.now() + datetime.timedelta(days=7),
        "date_responded": None
    }
    
    # In a real implementation, would add to database and send email
    return new_invitation

@router.put("/invitations/{invitation_id}/resend", response_model=Invitation)
async def resend_invitation(
    invitation_id: str
):
    """
    Resend an expired invitation.
    """
    invitation = next((i for i in sample_invitations if i["id"] == invitation_id), None)
    if not invitation:
        raise HTTPException(status_code=404, detail=f"Invitation with ID {invitation_id} not found")
    
    # In a real implementation, this would update the database and resend the email
    # For demo purposes, just returning the updated invitation
    updated_invitation = {
        **invitation,
        "status": "pending",
        "date_sent": datetime.now(),
        "date_expires": datetime.now() + datetime.timedelta(days=7),
        "date_responded": None
    }
    
    return updated_invitation

@router.delete("/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invitation(
    invitation_id: str
):
    """
    Cancel a pending invitation.
    """
    invitation = next((i for i in sample_invitations if i["id"] == invitation_id), None)
    if not invitation:
        raise HTTPException(status_code=404, detail=f"Invitation with ID {invitation_id} not found")
    
    # In a real implementation, this would delete from the database or mark as cancelled
    return None

@router.get("/roles", response_model=List[Role])
async def get_roles(
    organization_id: Optional[str] = Query(None, description="Organization ID")
):
    """
    Get the list of available user roles.
    """
    return sample_roles

@router.get("/roles/{role_id}", response_model=Role)
async def get_role(
    role_id: str = Path(..., description="Role ID")
):
    """
    Get detailed information about a specific role.
    """
    role = next((r for r in sample_roles if r["id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
    
    return role

@router.post("/roles", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    organization_id: str = Query(..., description="Organization ID")
):
    """
    Create a new custom role.
    """
    # In a real implementation, this would create a new role in the database
    # For demo purposes, returning a mock response
    new_id = str(len(sample_roles) + 1)
    new_role = {
        "id": new_id,
        **role.dict(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "user_count": 0
    }
    
    # In a real implementation, would add to database
    return new_role

@router.put("/roles/{role_id}", response_model=Role)
async def update_role(
    role_id: str,
    role_update: RoleBase
):
    """
    Update an existing role.
    """
    role = next((r for r in sample_roles if r["id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
    
    # Check if it's a default role that shouldn't be modified
    if role_id in ["1", "2", "3", "4"]:
        raise HTTPException(status_code=403, detail="Default roles cannot be modified")
    
    # In a real implementation, this would update the database
    # For demo purposes, just returning the updated role
    updated_role = {
        **role,
        **role_update.dict(),
        "updated_at": datetime.now()
    }
    
    return updated_role

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str
):
    """
    Delete a custom role.
    """
    role = next((r for r in sample_roles if r["id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found")
    
    # Check if it's a default role that shouldn't be deleted
    if role_id in ["1", "2", "3", "4"]:
        raise HTTPException(status_code=403, detail="Default roles cannot be deleted")
    
    # In a real implementation, this would delete from the database
    return None

@router.get("/permissions", response_model=List[Permission])
async def get_permissions():
    """
    Get the list of available permissions.
    """
    return sample_permissions

# Helper function
def get_default_permissions_for_role(role: UserRole) -> List[str]:
    """
    Returns the default permissions for a given role.
    """
    if role == UserRole.OWNER:
        return ["admin", "manage_team", "manage_billing", "edit_data", "view_data"]
    elif role == UserRole.MANAGER:
        return ["edit_data", "view_data", "export_reports"]
    elif role == UserRole.ANALYST:
        return ["view_data", "export_reports"]
    elif role == UserRole.MARKETING:
        return ["view_data"]
    else:
        return ["view_data"]  # Default for custom roles 