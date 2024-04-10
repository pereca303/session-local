from typing import List
from stream_data import StreamData
from shared_model.update_request import UpdateRequest
from stream_data import StreamData
from stream_category import StreamCategory
from mongoengine import connect, disconnect
from ipaddress import ip_address

from stream_registry.src.media_server_data import MediaServerData

def filter_region_streams(streams, region):
	stream: StreamData

	def region_filter(stream:StreamData):
		return stream.region == region

	for stream in streams:
		stream.media_servers = list(filter(region_filter, stream.media_servers ))
		
	return streams

class Db:

	def __init__(self, conn_string: str):
		connect(host=conn_string)

	def close(self):
		disconnect()
	
	def fetch_analytics(viewer: str):
		return []

	def recommended_sort_pipeline():
		return [{'$match': {}}]

	def views_sort_pipeline():
		return [{'$match': {}}]

	def no_sort_pipeline():
		return [{'$match': {}}]

	def from_stage(ind: int):
		return {'$skip': ind}

	def count_stage(count: int):
		return {'$limit': count}

	def dict_to_data(dict):
		return StreamData(**dict)

	def get_all(self, from_ind, cnt, region, ordering):

		pipeline = []

		if ordering == "Recommended":
			pipeline = Db.recommended_sort_pipeline()
		elif ordering == "Views": 
			pipeline = Db.views_sort_pipeline()
		else: 
			pipeline = Db.no_sort_pipeline()
		
		pipeline.append(Db.from_stage(from_ind))
		pipeline.append(Db.count_stage(cnt))
		

		# datas = StreamData.objects(media_servers__region=region)\
		# 	.skip(from_ind)\
		# 	.limit(cnt)

		return StreamData.objects().aggregate(pipeline)

		# return filter_region_streams(datas, region)

	def get_by_category(self, 
					category: StreamCategory, 
					region: str,
					start: int, 
					count: int) -> List[StreamData]:

		datas = StreamData.objects(category=category, 
							media_servers__region=region)\
					.skip(start)\
					.limit(count)
		return filter_region_streams(datas, region)

	def save_empty(self, creator: str, 
				ingest_ip: str, 
				stream_key: str) -> StreamData:
		
		return StreamData.empty(creator, ingest_ip, stream_key).save()

	def update(self, streamer: str, update_req: UpdateRequest) -> bool:
		update_result = StreamData\
			.objects(creator=streamer)\
			.update_one(set__title=update_req.title, 
			   		set__category=update_req.category,
					set__is_public=update_req.is_public)
		

		return update_result > 0
			
	def remove_stream(self, key:str):
		return StreamData.objects(stream_key=key).first().delete()

	def add_media_server(self, stream_creator: str, 
					quality: str,
					server_ip: str,
					region:str, 
					media_url:str) -> StreamData:
		
		stream:StreamData = StreamData.objects(creator=stream_creator).first()

		if stream is None:
			print(f"Failed to find stream with creator: {stream_creator} ...")
			return None
		
		new_server_data = MediaServerData(quality=quality, 
									ip=int(ip_address(server_ip)), 
									region=region, 
									media_url=media_url)
		
		stream.media_servers.append(new_server_data)
		save_res:StreamData = stream.save()

		return save_res
	
	def remove_media_server(self, stream_creator: str, server_ip: str) -> StreamData:

		stream:StreamData = StreamData.objects(creator=stream_creator).first()
		
		if stream is None:
			# This is normal. When stream is stopped, ingest server will 
			# send stop_stream request which will remove stream completely.
			# Remove media server is issued by the cdn a bit latter, when the 
			# last packet arrives from the ingest.
			print("Failed to find requested stream data.")
			return None

		int_addr = int(ip_address(server_ip))

		# Filter out the instance with ip == int_addr
		stream.media_servers = [ 
						data 
						for data in stream.media_servers 
						if data.ip != int_addr 
					]

		return stream.save()

	def get_stream(self, streamer) -> StreamData:
		return StreamData.objects(creator=streamer).first()
	
	def get_streams(self, streams: List[str], ordering: str = 'None'):
		

		return 