"""
    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.last_x is None:
            
            self.last_x = int((a0.x() - self.delta_x) / self.label_paint_w * self.imgW) 
            self.last_y = int((a0.y() - self.delta_y) / self.label_paint_h * self.imgH) 
            # self.last_x = int(a0.x() - self.delta_x)
            # self.last_y = int(a0.y() - self.delta_y)
            return # ignore the first frame
        
        self.drawX = int((a0.x() - self.delta_x) / self.label_paint_w * self.imgW) 
        self.drawY = int((a0.y() - self.delta_y) / self.label_paint_h * self.imgH) 
        
        
        
        


        if self.breakPointActive:
            ## find closest point on contour 

            ## Reload pixmap
            # Load skeletonized mask for editing
            rgb_image = cv2.cvtColor(self.seedObj.skeltonized, cv2.COLOR_BGR2RGB)
            imgPilMask = Image.fromarray(rgb_image).convert('RGB')        
            imMask = ImageQt(imgPilMask).copy()
            self.canvasMask= QtGui.QPixmap.fromImage(imMask)
            self.customLabel.setPixmap(QPixmap.fromImage(ImageQt(imgPilMask)))
            painter = QtGui.QPainter(self.canvasMask)
            
            # SET PEN
            p = painter.pen()

            closest_point_cnt = find_closest_point(contour=self.seedObj.sorted_point_list, point = (self.drawY, self.drawX))
            self.pen_color_mask = QtGui.QColor('blue')
            p.setWidth(20)
            p.setColor(self.pen_color_mask)
            painter.setPen(p)
            qPoint = QPoint(closest_point_cnt[1], closest_point_cnt[0])
            painter.drawPoint(qPoint)
            painter.end()
            self.customLabel.setPixmap(self.canvasMask)
            self.update()

            self.seedObj.reassign_points(new_break_point=closest_point_cnt)
            self.setColorPixmap()
            self.last_x = self.drawX
            self.last_y = self.drawY
            
        
        if self.eraserActive:

            ################ paint mask ###################
            
            painter = QtGui.QPainter(self.canvasMask)
           

            # SET PEN
            p = painter.pen()
            p.setWidth(self.pen_thickness)
            p.setColor(self.pen_color_mask)
            painter.setPen(p)
            
            # print('a0', a0.x(), a0.y())


            # self.drawX = int((a0.x() - self.delta_x) / self.label_paint_w * self.imgW) 
            # self.drawY = int((a0.y() - self.delta_y) / self.label_paint_h * self.imgH) 
            # self.drawX = int(a0.x() - self.delta_x)
            # self.drawY = int(a0.y() - self.delta_y)

        
            painter.drawLine(self.last_x, self.last_y, self.drawX, self.drawY)
            painter.end()
            self.label_img_seed_mask.setPixmap(self.canvasMask)
            self.update()
            
            
            ################ paint MainImg ###################

            # painter1 = QtGui.QPainter(self.canvas)
        

            # # SET PEN
            # p1 = painter1.pen()
            # p1.setWidth(self.pen_thickness)
            # p1.setColor(self.pen_color_img)
            # # painter1.setBrush(QtGui.QColor(0, 255, 0, 200))
            # painter1.setPen(p1)

            # self.drawX = int(a0.x() / self.label_paint_w * self.imgW)
            # self.drawY = int(a0.y() / self.label_paint_h * self.imgH)

        
            # painter1.drawLine(self.last_x, self.last_y, self.drawX, self.drawY)
            # painter1.end()
            # # self.label_img_org.setPixmap(self.canvas)
            # self.update()
            
            self.seedObj.erase_points(point=[self.drawY, self.drawX])

            self.setColorPixmap()
            # update origin
            self.last_x = self.drawX
            self.last_y = self.drawY


        self.update_values()

        return super().mouseMoveEvent(a0)
    """
    # def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
    #     self.last_x = None
    #     self.last_y = None

    #     return super().mouseReleaseEvent(a0)