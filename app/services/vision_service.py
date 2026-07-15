from app.domain.photo_models import PhotoAnalysis, ProcessedPhoto


class VisionService:
    def analyze_photos(self, photos: list[ProcessedPhoto]) -> list[PhotoAnalysis]:
        return [self._analyze_one(photo, index) for index, photo in enumerate(photos)]

    def _analyze_one(self, photo: ProcessedPhoto, index: int) -> PhotoAnalysis:
        filename = photo.original_filename.lower()
        photo_type = self._classify(filename, index)
        confidence = 0.5 if "low" in filename or "low" in photo.photo_id else 0.9
        warnings: list[str] = []
        if confidence < 0.6:
            warnings.append("照片分析置信度较低，需要人工确认。")

        visible_date = None
        visible_time = None
        if photo.exif_datetime:
            date_part, time_part = photo.exif_datetime.split(" ", 1)
            visible_date = date_part.replace(":", "-", 2)
            visible_time = time_part[:5]

        if "conflict" in filename and photo.exif_datetime:
            visible_time = "10:00"
            exif_time = photo.exif_datetime.split(" ", 1)[1][:5]
            if visible_time != exif_time:
                warnings.append("EXIF 时间与画面时间不一致，需要人工确认。")

        return PhotoAnalysis(
            photo_id=photo.photo_id,
            original_filename=photo.original_filename,
            exif_datetime=photo.exif_datetime,
            visible_date=visible_date,
            visible_time=visible_time,
            visible_location="现场" if photo_type == "工作现场" else None,
            photo_type=photo_type,
            description=f"Fake Vision 判断为{photo_type}。",
            confidence=confidence,
            warnings=warnings,
        )

    def _classify(self, filename: str, index: int) -> str:
        if "departure" in filename or "start" in filename:
            return "出发打卡"
        if "arrival" in filename:
            return "到达现场"
        if "leave" in filename:
            return "离开现场"
        if "hotel" in filename:
            return "到达酒店"
        if "site" in filename:
            return "工作现场"
        fallback = ["出发打卡", "工作现场", "到达酒店", "其他"]
        return fallback[min(index, len(fallback) - 1)]
