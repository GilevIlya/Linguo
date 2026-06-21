from logging import getLogger
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from api.v1.models import User
from api.v1.repositories.interfaces.IUserRepository import IUserRepository
from api.v1.services.exceptions.base_exceptions import AlreadyExistsException, NotFoundException
from api.v1.services.exceptions.error_codes.user_error_codes import UserErrorCodes

logger = getLogger("app")


class UserService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def create_user(self, user: User) -> User:
        """
        Create a new user.
        Args:
            user: User entity to create
        Returns:
            Created user entity
        Raises:
            AlreadyExistsException: If user with this email already exists
        """
        try: # TODO: проверку на то что емейл норм
            return await self.user_repository.create(user)
        except IntegrityError as e:
            logger.error("Failed to create user: %s", e)
            raise AlreadyExistsException(
                error_code=UserErrorCodes.EMAIL_ALREADY_IN_USE.value,
                message="User with this email already exists"
            )

    async def get_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.

        :param email: The email address of the user to retrieve.
        :return User: The user entity if found.
        :raise NotFoundException: If no user with the given email is found.
        """
        if user :=  await self.user_repository.find_by_email(email):
            return user
        raise NotFoundException(UserErrorCodes.USER_NOT_FOUND.value, message="User with this email not found")

    async def get_by_id(self, user_id: UUID) -> User:
        """
        Retrieve a user by their unique ID.

        :param user_id: The unique identifier of the user to retrieve.
        :return User: The user entity if found.
        :raise NotFoundException: If no user with the given ID is found.
        """
        if user := await self.user_repository.get_by_id(user_id):
            if user.deleted_at:
                logger.warning("Attempt to access soft deleted user with ID %s", user_id)
                raise NotFoundException(UserErrorCodes.USER_NOT_FOUND.value, message="User with this ID not found")
            return user
        raise NotFoundException(UserErrorCodes.USER_NOT_FOUND.value, message="User with this ID not found")

    async def update_password(self, user: User, hashed_password: str) -> User:
        """Persist a new hashed password for a user."""
        updated = await self.user_repository.update(user, {"password": hashed_password})
        if not updated:
            raise NotFoundException(UserErrorCodes.USER_NOT_FOUND.value, message="User with this ID not found")
        return updated

