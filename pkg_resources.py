"""
Minimal pkg_resources shim for environments where setuptools is not available (e.g., Vercel with Python 3.12+).

The PhonePe SDK depends on apscheduler which imports:
    from pkg_resources import iter_entry_points

This shim provides just enough to satisfy that import using importlib.metadata (stdlib).
"""

import importlib.metadata


def iter_entry_points(group, name=None):
    """Yield entry points for the given group, optionally filtered by name."""
    try:
        eps = importlib.metadata.entry_points()
        # Python 3.12+ returns a SelectableGroups or dict-like
        if hasattr(eps, 'select'):
            selected = eps.select(group=group)
        elif isinstance(eps, dict):
            selected = eps.get(group, [])
        else:
            selected = [ep for ep in eps if ep.group == group]

        for ep in selected:
            if name is None or ep.name == name:
                yield ep
    except Exception:
        return


def get_distribution(dist_name):
    """Get distribution info for a package."""
    try:
        dist = importlib.metadata.distribution(dist_name)
        return _DistInfo(dist)
    except importlib.metadata.PackageNotFoundError:
        raise DistributionNotFound(dist_name)


class _DistInfo:
    """Minimal Distribution wrapper."""
    def __init__(self, dist):
        self._dist = dist
        self.version = dist.version
        self.project_name = dist.metadata["Name"]

    def __str__(self):
        return f"{self.project_name} {self.version}"


class DistributionNotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


def require(*args, **kwargs):
    """No-op require."""
    pass


def resource_filename(package, resource):
    """Minimal resource_filename."""
    import os
    try:
        mod = __import__(package)
        return os.path.join(os.path.dirname(mod.__file__), resource)
    except Exception:
        return resource
