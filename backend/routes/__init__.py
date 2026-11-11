"""Route blueprints, one file per role."""

from .auth import bp as auth_bp
from .options import bp as options_bp
from .student import bp as student_bp
from .scholar import bp as scholar_bp
from .editor import bp as editor_bp
from .admin import bp as admin_bp

__all__ = ["auth_bp", "options_bp", "student_bp", "scholar_bp",
           "editor_bp", "admin_bp"]
