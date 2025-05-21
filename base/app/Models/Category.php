<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Category extends Model
{
    use HasFactory, SoftDeletes;
    protected $table = 'categories';
    protected $guarded = [];
    protected $date = ['deleted_at'];

    public function topics()
    {
        return $this->hasMany(Topic::class);
    }
}
