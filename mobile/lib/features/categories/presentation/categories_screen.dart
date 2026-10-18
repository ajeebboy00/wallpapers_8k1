import 'package:flutter/material.dart';

class CategoriesScreen extends StatelessWidget {
  const CategoriesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Categories', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: const Center(
        child: Text('Categories Grid & Discovery', style: TextStyle(color: Colors.grey)),
      ),
    );
  }
}
