import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AddMachineComponent } from './add-machine/add-machine.component';
import { ShowStatsComponent } from './show-stats/show-stats.component';

const routes: Routes = [
  { path: '', component: AddMachineComponent},
  { path: 'stats', component: ShowStatsComponent},
  
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})

export class AppRoutingModule { }

export const routingComponents = [
  AddMachineComponent,
  ShowStatsComponent,
]
