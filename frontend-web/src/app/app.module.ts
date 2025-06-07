// This file is no longer needed when using standalone components and bootstrapApplication.
// You can delete this file or leave it empty if you have migrated to standalone bootstrap.
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { AppComponent } from './app.component';
import { LoginComponent } from './pages/login/login.component';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [],
  imports: [
    BrowserModule,
    CommonModule,
    AppComponent,
    LoginComponent,
    HttpClientModule
   ],
   
 })
export class AppModule {}