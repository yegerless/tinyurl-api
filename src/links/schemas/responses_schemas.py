from pydantic import BaseModel, Field



class PostShortenLinkResponse(BaseModel):
    pass



class RedirectOnFullLinkResponse(BaseModel):
    pass



class DeleteShortLinkResponse(BaseModel):
    pass 



class UpdateShortLinkResponse(BaseModel):
    pass 



class GetShortLinkStatisticsResponse(BaseModel):
    pass



class GetShortLinkByOriginalUrlResponse(BaseModel):
    pass 
