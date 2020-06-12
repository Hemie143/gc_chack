import LatLon23

class LatLonGC(LatLon23.LatLon):

    def __init__(self, lat, lon, name=None):
        super().__init__(lat, lon, name=name)

    def to_gc(self):
        # Format : N5057631E00410274
        lat_min = int(float(self.lat.to_string('M')) * 1000) / 1000
        lon_min = int(float(self.lon.to_string('M')) * 1000) / 1000
        lat_min_c = f'{lat_min:06.3f}'.replace('.', '')
        lon_min_c = f'{lon_min:06.3f}'.replace('.', '')
        '''
        result = f'{self.lat_hemi}{self.lat_deg:02}{lat_min_c}{self.lon_hemi}{self.lon_deg:03}{lon_min_c}'
        if len(result) != 17:
            print(result)
            print(self.point.__dict__)
            print(self.point.lat.__dict__)
            print(self.point.lon.__dict__)
            print(lon_min_c)
            print(f'{self.lon_min:06.3f}')
            print(f'{self.lon_min:02.3f}'.replace('.', ''))
        '''


# TODO: Create similar class with circle
class Coords_shape:
    # TODO: Pass only central point and distance

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        # TODO: Could probably be optimized
        borders = self.get_borders()
        self.border_south = borders['south']
        self.border_north = borders['north']
        self.border_west = borders['west']
        self.border_east = borders['east']
        self.point = LatLonGC(self.border_south, self.border_west)
        # self.checker = self.point.to_string('')
        self.lat_hemi = self.point.lat.to_string('H')
        self.lat_deg = int(self.point.lat.to_string('d'))
        self.lat_min = int(float(self.point.lat.to_string('M')) * 1000) / 1000
        self.lon_hemi = self.point.lon.to_string('H')
        self.lon_deg = int(self.point.lon.to_string('d'))
        self.lon_min = int(float(self.point.lon.to_string('M')) * 1000) / 1000
        self.pointchecker = self.to_gc()

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError

    def to_gc(self):
        # Format : N5057631E00410274
        lat_min_c = f'{self.lat_min:06.3f}'.replace('.', '')
        lon_min_c = f'{self.lon_min:06.3f}'.replace('.', '')
        result = f'{self.lat_hemi}{self.lat_deg:02}{lat_min_c}{self.lon_hemi}{self.lon_deg:03}{lon_min_c}'
        if len(result) != 17:
            print(result)
            print(self.point.__dict__)
            print(self.point.lat.__dict__)
            print(self.point.lon.__dict__)
            print(lon_min_c)
            print(f'{self.lon_min:06.3f}')
            print(f'{self.lon_min:02.3f}'.replace('.', ''))

            exit()
        return result

    def get_borders(self):
        # For a 2-mile radius, this will generate a list of 19.088.055 coordinates in a rectangle and
        # 14.991.897 coordinates in a circle
        # distance = 0.1
        # For a 100 meter radius, this will generate a list of 17575 coordinates
        border = {}
        border['north'] = self.center.offset(0, self.radius).lat              # N50° 59.572' E004° 10.188'
                                                                      # N50° 57.890' E004° 10.188    (0.1)
        # print(border_north.to_string('H% %d%° %M'))
        # print(border_north.__dict__)
        # print(border_north.to_string('%d%° %M'))
        # print(border_north.decimal_minute)
        # border_north = f'{border_north.degree}'

        border['east'] = self.center.offset(90, self.radius).lon              # N50° 57.836' E004° 10.273    (0.1)
        # print(border_east.__dict__)

        border['south'] = self.center.offset(180, self.radius).lat            # N50° 57.782' E004° 10.188'   (0.1)
        # print(border_south.__dict__)

        border['west'] = self.center.offset(270, self.radius).lon             # N50° 57.836' E004° 10.103'
        # print(border_west.__dict__)
        return border

class Coords_square(Coords_shape):

    def __next__(self):
        # TODO: Change of hemisphere ?
        self.lon_min += 0.001
        if self.lon_min >= 60.0:
            self.lon_min = 0.0
            # TODO: something's wrong here
            self.lon_deg += 1
        coord_lon = f'{self.lon_hemi} {self.lon_deg} {self.lon_min}'
        self.lon = LatLon23.string2geocoord(coord_lon, LatLon23.Longitude, 'H% %d% %M')
        # TODO: Fix mess between lat and lon
        # TODO: no need of decimal degree in next line ???
        if self.lon.decimal_degree >= self.border_east.decimal_degree:
            self.lon = self.border_west
            self.lon_min = int(self.border_west.decimal_minute * 1000) / 1000
            self.lon_deg = int(self.border_west.degree)
            self.lat_min += 0.001
            if self.lat_min >= 60.0:
                self.lat_min = 0.0
                self.lat_deg += 1
        # TODO: if latitude reaches border_north: raise StopIteration()
        coord_lat = f'{self.lat_hemi} {self.lat_deg} {self.lat_min}'
        self.lat = LatLon23.string2geocoord(coord_lat, LatLon23.Latitude, 'H% %d% %M')
        if self.lat.decimal_degree > self.border_north.decimal_degree:
            raise StopIteration()
        self.point = LatLonGC(self.lat, self.lon)
        self.pointchecker = self.to_gc()
        # distance = self.point.distance(self.center)
        # print(distance, '  ', self.point)
        '''
        if self.lon_min > self.border_east:
            self.lon_min = self.border_west
            self.lat_min += 0.001
        '''
        # return (self.to_gc(), distance)
        # return (self.to_gc())
        return (self.point, self.pointchecker)


class Coords_circle(Coords_shape):

    def __next__(self):
        outsideCircle= True
        while outsideCircle:
            # TODO: Change of hemisphere ?
            self.lon_min += 0.001
            if self.lon_min >= 60.0:
                self.lon_min = 0.0
                # TODO: something's wrong here
                self.lon_deg += 1
            coord_lon = f'{self.lon_hemi} {self.lon_deg} {self.lon_min}'
            self.lon = LatLon23.string2geocoord(coord_lon, LatLon23.Longitude, 'H% %d% %M')
            # TODO: Fix mess between lat and lon
            # TODO: no need of decimal degree in next line ???
            if self.lon.decimal_degree >= self.border_east.decimal_degree:
                self.lon = self.border_west
                self.lon_min = int(self.border_west.decimal_minute * 1000) / 1000
                self.lon_deg = int(self.border_west.degree)
                self.lat_min += 0.001
                if self.lat_min >= 60.0:
                    self.lat_min = 0.0
                    self.lat_deg += 1
            # TODO: if latitude reaches border_north: raise StopIteration()
            coord_lat = f'{self.lat_hemi} {self.lat_deg} {self.lat_min}'
            self.lat = LatLon23.string2geocoord(coord_lat, LatLon23.Latitude, 'H% %d% %M')
            if self.lat.decimal_degree > self.border_north.decimal_degree:
                raise StopIteration()
            self.point = LatLonGC(self.lat, self.lon)

            distance = self.point.distance(self.center)
            outsideCircle = distance > self.radius

        self.pointchecker = self.to_gc()
        # distance = self.point.distance(self.center)
        # print(distance, '  ', self.point)
        '''
        if self.lon_min > self.border_east:
            self.lon_min = self.border_west
            self.lat_min += 0.001
        '''
        # return (self.to_gc(), distance)
        # return (self.to_gc())
        return (self.point, self.pointchecker)

