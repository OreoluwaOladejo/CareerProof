
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# This is our SQLAlchemy data model.
from app.models.skill import Skill
from app.models.user import User
# These are our Pydantic schemas.
from app.schemas.skill import SkillCreate, SkillUpdate

# CUSTOM ERRORS
# This error means the skill either does not exist
# or does not belong to the currently logged-in user.
class SkillNotFound(Exception):
    pass

# This error means the user already has a skill with this name.
class SkillAlreadyExists(Exception):
    pass

# CHECK IF A SKILL NAME ALREADY EXISTS
'''Receive the user's ID and the skill name.
Search the skills belonging to that user.
db- Database session 
By passing the current skill's ID as exclude_skill_id=5, you tell the query:
"Check if 'Python' exists for this user, but ignore record ID 5 which we know already 
has python '''
def check_skill_name_exists(
    db: Session,
    user_id: int,
    skill_name: str,
    exclude_skill_id: int | None = None,
):
    statement = select(Skill.id).where(
        Skill.user_id == user_id,
        func.lower(Skill.name) == skill_name.lower() )
    if exclude_skill_id is not None:
        statement = statement.where(
            Skill.id != exclude_skill_id)
    #First skill we find already tells us that it is a duplicate   
    existing_skill = db.scalars(statement).first()
    return existing_skill is not None


# CREATE A NEW SKILL
def create_skill(
    db: Session,
    current_user: User,
    skill_data: SkillCreate,
):
    # Check whether this user already has a skill with this name.
    if check_skill_name_exists(
        db,
        current_user.id,
        skill_data.name,
    ):
        raise SkillAlreadyExists()

    # Create a new skill.
    skill = Skill(
        user_id=current_user.id,
        name=skill_data.name,
        category=skill_data.category,
        proficiency=skill_data.proficiency,
    )

    # Add the skill to the database session.
    db.add(skill)

    # Save the skill permanently.
    try:
        db.commit()

    except IntegrityError:
        # Undo the failed database transaction.
        db.rollback()

        # Return our custom duplicate error.
        raise SkillAlreadyExists()

    # Reload the skill to get generated database values.
    db.refresh(skill)

    # Return the newly created skill.
    return skill


# GET ALL SKILLS BELONGING TO THE CURRENT USER
def get_all_skills(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
):
    # Get only the skills belonging to the logged-in user.
    statement = select(Skill).where(
        Skill.user_id == current_user.id
    )

    # If a search term was provided, filter the skill names.
    if search:
        statement = statement.where(
            Skill.name.icontains(
                search,
                autoescape=True
            )
        )

    # Arrange skills alphabetically.
    # Use the ID as a secondary sorting rule.
    statement = statement.order_by(
        func.lower(Skill.name),
        Skill.id
    )

    # Pagination:
    # skip determines how many records to skip.
    # limit determines the maximum number of records to return.
    statement = statement.offset(skip).limit(limit)

    # Execute the query and collect all matching skills.
    skills = db.scalars(statement).all()

    # Return the skills.
    return list(skills)


# GET ONE SKILL BY ID
def get_skill_by_id(
    db: Session,
    current_user: User,
    skill_id: int,
):
    # Search for a skill whose ID matches skill_id
    # AND whose owner is the currently logged-in user.
    statement = select(Skill).where(
        Skill.id == skill_id,
        Skill.user_id == current_user.id
    )

    # Execute the query.
    skill = db.execute(statement).scalar_one_or_none()

    # If the skill does not exist, or belongs to another user,
    # raise our custom error.
    if skill is None:
        raise SkillNotFound()

    # Return the skill.
    return skill


# UPDATE AN EXISTING SKILL
def update_skill(
    db: Session,
    current_user: User,
    skill_id: int,
    skill_data: SkillUpdate,
):
    # First, retrieve the skill.
    # This also checks that the skill belongs to the current user.
    skill = get_skill_by_id(
        db,
        current_user,
        skill_id
    )

    # Get ONLY the fields the client actually submitted.
    # This is important for PATCH requests.
    changes = skill_data.model_dump(exclude_unset=True)

    # Check whether the user is trying to change the skill name.
    if "name" in changes:

        # Check whether another skill already has this name.
        if check_skill_name_exists(
            db,
            current_user.id,
            changes["name"],
            exclude_skill_id=skill.id
        ):
            raise SkillAlreadyExists()

        # Update the skill name.
        skill.name = changes["name"]

    # Update the category if the client submitted it.
    if "category" in changes:
        skill.category = changes["category"]

    # Update proficiency if the client submitted it.
    if "proficiency" in changes:
        skill.proficiency = changes["proficiency"]

    # Save the changes permanently.
    try:
        db.commit()

    except IntegrityError:
        # Undo the failed transaction.
        db.rollback()

        raise SkillAlreadyExists()

    # Reload the skill to get updated database values.
    db.refresh(skill)

    # Return the updated skill.
    return skill


# DELETE AN EXISTING SKILL
def delete_skill(
    db: Session,
    current_user: User,
    skill_id: int,
):
    # First, retrieve the skill.
    # This ensures the skill belongs to the current user.
    skill = get_skill_by_id(
        db,
        current_user,
        skill_id
    )

    # Delete the skill from the database.
    db.delete(skill)

    # Save the deletion permanently.
    db.commit()
