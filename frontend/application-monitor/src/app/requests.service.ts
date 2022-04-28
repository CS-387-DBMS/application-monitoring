// import { Injectable } from '@angular/core';

// @Injectable({
//   providedIn: 'root'
// })
// export class RequestsService {

//   constructor() { }
// }

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class RequestsService {

  private BASE:string = 'http://localhost:8000'

  public get(url:string){
    return this.http.get<JSON>(this.BASE+url)
  }

  public post(url:string, body: any){
    return this.http.post(this.BASE+url, body)
  }

  public del(url:string, id: number){
   return this.http.post(this.BASE+url, {'id' : id})
  }

  constructor(private http: HttpClient) { }
}