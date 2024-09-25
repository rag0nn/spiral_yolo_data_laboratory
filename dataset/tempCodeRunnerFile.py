def change_data(self,index):
        data = self.sectF.buttons[index].data
        if data is not None:
            self.chosen_data = data
            self.old_chosen_data_index = self.chosen_data_index
            self.chosen_data_index = index

            image = cv2.imread(self.chosen_data.image_path)
            image = self.paint_objects(image,data)
            image = self._numpy_to_qpixmap(image)
            image = image.scaled(int(QGuiApplication.primaryScreen().geometry().width()*0.7),int(QGuiApplication.primaryScreen().geometry().height()*0.6))
            self.sectC.image.setPixmap(image)
            self.sectE.load_data_info(data)
            self.sectE.data = data
            self.sectE.title.setText("DATA: " + data.data_name)
            self.sectF.buttons[self.chosen_data_index].color_mark()
            self.sectF.buttons[self.old_chosen_data_index].color_mark_remove()
        else:
            pass