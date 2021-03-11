# -*- coding: utf-8 -*-
from Products.Five import BrowserView


class View(BrowserView):
    def get_children(self):
        return [self.wrap_obj(x) for x in self.context.listFolderContents()]

    def wrap_obj(self, item):
        url = item.absolute_url()
        if item.portal_type == "File":
            file_obj = getattr(item, "file", None)
            if file_obj:
                url = "{}/@@download/file/{}".format(url, file_obj.filename)
        return {
            "url": url,
            "title": item.Title(),
            "description": item.Description() or item.Title(),
        }
