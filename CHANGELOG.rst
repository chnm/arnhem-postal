Change Log
==========

1.0 
---

- Merge design changes into ``main`` branch.
- Update README with new instructions.

0.8
---

- Implementation of django_tables2 for displaying postal objects.
- First draft of a working map interface. 
- Derive postal routes by calculating the path a postal object travels (sender, postmark, censor, recipient).

0.7
---

- Implementation of data importing script.
- Implementation of image importing script.

0.4
---

- Added starter templates for the homepage, about page, and object display.
- Updated model to account for related images.
- Updated model to account for a collection an individual object belongs to.
- Migrated AuthUser to AllAuth.

0.3
---

- Initial scaffolding and data model setup. This is a work in progress and is not yet ready for use.
- The project runs a custom AuthUserModel for getting started,
  provided by [django-authuser](https://github.com/sesh/django-authuser).
