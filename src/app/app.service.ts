import { catchError, map } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AppService {

  constructor(private http: HttpClient) { }

  getResponse(prompt: string) {
    return this.http.post<string>('http://localhost:5000/api/ask', {
      prompt
    }).pipe(
      map((response) => {
        console.log(response);
        return 'test'
      }),
      catchError(() => ['Something went wrong.'])
    );
  }
}
